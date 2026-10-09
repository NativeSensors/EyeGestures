use crate::clock::{interval_from_fps, system_clock, NowFn, DEFAULT_SAMPLING_FPS};
use crate::{Calibrator, euclidean_distance};

pub struct GazeResult {
    pub x: f64,
    pub y: f64,
    pub calibrating: bool,
    pub calib_point: [f64; 2],
}

/// Tolerance when comparing elapsed time against the sampling interval. Without it a camera
/// running at exactly the sampling rate drops every other frame to float rounding.
const SAMPLING_EPSILON_MS: f64 = 1e-6;

/// Shared core gaze tracking logic (wasm + python)
pub struct EyeGesturesCore {
    pub calibrator: Calibrator,
    pub screen_width: f64,
    pub screen_height: f64,
    pub calib_counter: usize,
    pub calib_max: usize,
    pub dynamic_recalib: bool,
    /// Samples (not frames) accepted while the gaze stayed on the current calibration point.
    pub samples_on_point: usize,
    pub prev_calib: [f64; 2],
    pub eye_calib_regions: Vec<[f64; 2]>,
    pub buffer: Vec<[f64; 2]>,
    pub start_width: f64,
    pub start_height: f64,
    pub head_start: [f64; 2],
    pub last_keypoints: Vec<f64>,
    /// Calibration data acquisition rate in samples per second. `<= 0.0` samples every frame.
    pub sampling_fps: f64,
    /// Total number of calibration samples accepted so far.
    pub samples_taken: usize,
    last_sample_ms: Option<f64>,
    now_ms: NowFn,
}

impl EyeGesturesCore {
    pub fn new(screen_width: f64, screen_height: f64, dynamic_recalib: bool) -> Self {
        Self::new_with_clock(
            screen_width,
            screen_height,
            dynamic_recalib,
            DEFAULT_SAMPLING_FPS,
            system_clock(),
        )
    }

    /// Same as `new` but with an explicit calibration sampling rate and an injectable clock.
    /// `sampling_fps <= 0` disables the cap. `now_ms` lets tests drive time deterministically.
    pub fn new_with_clock(
        screen_width: f64,
        screen_height: f64,
        dynamic_recalib: bool,
        sampling_fps: f64,
        now_ms: NowFn,
    ) -> Self {
        Self {
            calibrator: Calibrator::new(),
            screen_width,
            screen_height,
            calib_counter: 0,
            calib_max: 25,
            dynamic_recalib: dynamic_recalib,
            samples_on_point: 0,
            prev_calib: [0.0, 0.0],
            eye_calib_regions: vec![],
            buffer: vec![],
            start_width: 0.0,
            start_height: 0.0,
            head_start: [0.0, 0.0],
            last_keypoints: vec![],
            sampling_fps,
            samples_taken: 0,
            last_sample_ms: None,
            now_ms,
        }
    }

    /// Cap the calibration data acquisition to `sampling_fps` samples per second.
    /// `<= 0` disables the cap. Gaze tracking itself keeps running at the full frame rate.
    pub fn set_sampling_fps(&mut self, sampling_fps: f64) {
        self.sampling_fps = sampling_fps;
    }

    /// Current sampling rate in samples per second, `0.0` when the cap is disabled.
    pub fn sampling_fps(&self) -> f64 {
        if self.sampling_fps > 0.0 {
            self.sampling_fps
        } else {
            0.0
        }
    }

    /// Enable/disable dynamic recalibration at runtime.
    /// When disabled the tracker keeps its current calibration and never asks for new points.
    pub fn set_dynamic_recalib(&mut self, dynamic_recalib: bool) {
        self.dynamic_recalib = dynamic_recalib;
    }

    /// Whether dynamic recalibration is currently enabled.
    pub fn dynamic_recalib(&self) -> bool {
        self.dynamic_recalib
    }

    pub fn process_landmarks(&mut self, landmarks: &[[f64; 2]]) -> GazeResult {
        let left_indices  = [33, 133, 160, 159, 158, 157, 173, 155, 154, 153, 144, 145, 153, 246, 468];
        let right_indices = [362, 263, 387, 386, 385, 384, 398, 382, 381, 380, 374, 373, 374, 466, 473];

        let offset_x = landmarks.iter().map(|l| l[0]).fold(f64::INFINITY, f64::min);
        let offset_y = landmarks.iter().map(|l| l[1]).fold(f64::INFINITY, f64::min);
        let max_x    = landmarks.iter().map(|l| l[0]).fold(f64::NEG_INFINITY, f64::max);
        let max_y    = landmarks.iter().map(|l| l[1]).fold(f64::NEG_INFINITY, f64::max);
        let width  = max_x - offset_x;
        let height = max_y - offset_y;

        if self.start_width * self.start_height == 0.0 {
            self.start_width = width;
            self.start_height = height;
        }

        let scale_x = width / self.start_width;
        let scale_y = height / self.start_height;

        if self.head_start == [0.0, 0.0] {
            self.head_start = [offset_x * scale_x, offset_y * scale_y];
        }

        let to_coords = |indices: &[usize]| -> Vec<[f64; 2]> {
            indices.iter().map(|&i| {
                let l = landmarks[i];
                [((l[0] - offset_x) / width) * scale_x,
                 ((l[1] - offset_y) / height) * scale_y]
            }).collect()
        };

        let left_eye  = to_coords(&left_indices);
        let right_eye = to_coords(&right_indices);

        let mut keypoints: Vec<f64> = left_eye.iter().chain(right_eye.iter())
            .flat_map(|p| [p[0], p[1]])
            .collect();
        keypoints.extend([scale_x, scale_y, width, height]);
        keypoints.extend([
            offset_x * scale_x - self.head_start[0],
            offset_y * scale_y - self.head_start[1],
        ]);

        self.last_keypoints = keypoints.clone();

        let raw = self.calibrator.predict(&keypoints);
        self.buffer.push(raw);
        if self.buffer.len() > 20 {
            self.buffer.remove(0);
        }
        let point = self.buffer.iter().fold([0.0, 0.0], |acc, p| [acc[0] + p[0], acc[1] + p[1]]);
        let point = [point[0] / self.buffer.len() as f64, point[1] / self.buffer.len() as f64];

        let calibrating = self.calib_counter < self.calib_max;
        let calib_point = self.calibrator.current_point(self.screen_width, self.screen_height);

        if calibrating {
            // Tracker-side bookkeeping stays per-frame, only data acquisition is throttled.
            self.eye_calib_regions.push(left_eye[0]);

            let now = (self.now_ms)();
            let interval_ms = interval_from_fps(self.sampling_fps);
            let due = match self.last_sample_ms {
                None => true,
                Some(previous) => (now - previous).max(0.0) + SAMPLING_EPSILON_MS >= interval_ms,
            };

            if due {
                self.last_sample_ms = Some(now);
                self.samples_taken += 1;
                self.calibrator.add(keypoints, calib_point);

                let dist = euclidean_distance(&point, &calib_point);
                if dist < 0.1 * self.screen_width && self.samples_on_point > 20 {
                    self.calibrator.next_point();
                    self.samples_on_point = 0;
                    self.buffer.clear();
                } else if dist < 0.1 * self.screen_width {
                    self.samples_on_point += 1;
                }

                if self.prev_calib != calib_point {
                    self.prev_calib = calib_point;
                    self.calib_counter += 1;
                }
            }
        } else {
            let eye_calib_radius = 0.01;
            let seen = self.eye_calib_regions.iter()
                .any(|r| euclidean_distance(r, &left_eye[0]) < eye_calib_radius);

            if !seen && self.dynamic_recalib{
                self.calib_max += 5;
            }
        }

        let x = point[0].clamp(0.0, self.screen_width);
        let y = point[1].clamp(0.0, self.screen_height);

        GazeResult { x, y, calibrating, calib_point }
    }

    pub fn add_calibration_point(&mut self, x: f64, y: f64) {
        self.calib_counter += 1;
        self.calib_max += 1;
        self.calibrator.add(self.last_keypoints.clone(), [x, y]);
    }

    pub fn recalibrate(&mut self) {
        self.calibrator.reset();
        self.calib_counter = 0;
        self.samples_on_point = 0;
        self.samples_taken = 0;
        self.last_sample_ms = None;
    }
}
