use crate::eyegestures::EyeGesturesCore;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct EyeGesturesEngineWasm{
    core: EyeGesturesCore,
}

#[wasm_bindgen]
impl EyeGesturesEngineWasm {
    #[wasm_bindgen(constructor)]
    pub fn new(screen_width: f64, screen_height: f64, dynamic_recalib: bool) -> Self {
        Self{
            core: EyeGesturesCore::new(screen_width, screen_height, dynamic_recalib),
        }
    }

    pub fn process(&mut self, landmarks: Vec<f64>) -> Vec<f64> {
        let landmarks: Vec<[f64; 2]> = landmarks
            .chunks_exact(2)
            .map(|pair| [pair[0], pair[1]])
            .collect();

        let result = self.core.process_landmarks(&landmarks);
        vec![
            result.x,
            result.y,
            if result.calibrating { 1.0 } else { 0.0 },
            result.calib_point[0],
            result.calib_point[1],
        ]
    }

    /// Cap the calibration data acquisition to `sampling_fps` samples per second.
    /// `<= 0` disables the cap. Gaze tracking keeps running at the full frame rate.
    pub fn set_sampling_fps(&mut self, sampling_fps: f64) {
        self.core.set_sampling_fps(sampling_fps);
    }

    /// Get the current calibration sampling rate, `0.0` when the cap is disabled
    #[wasm_bindgen(getter)]
    pub fn sampling_fps(&self) -> f64 {
        self.core.sampling_fps()
    }

    /// Number of calibration samples accepted so far (capped by `sampling_fps`)
    #[wasm_bindgen(getter)]
    pub fn samples_taken(&self) -> usize {
        self.core.samples_taken
    }

    pub fn add_calibration_point(&mut self, x: f64, y: f64) {
        self.core.add_calibration_point(x, y);
    }

    pub fn recalibrate(&mut self) {
        self.core.recalibrate();
    }
}
