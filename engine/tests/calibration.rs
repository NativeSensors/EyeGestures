// Synthetic-data tests for the reservoir-based calibrator (V5).
// These verify that calibration runs end-to-end without crashing, that predictions stay
// finite (no saturation), and that the tracker actually advances through calibration points.

use EyegesturesEngine::{Calibrator, EyeGesturesCoreV5};

const SCREEN_W: f64 = 1920.0;
const SCREEN_H: f64 = 1080.0;

/// Eye-landmark indices used by `EyeGesturesCoreV5::process_landmarks`.
const LEFT_EYE: [usize; 14] = [33, 133, 160, 159, 158, 157, 173, 155, 154, 153, 144, 145, 153, 246];
const RIGHT_EYE: [usize; 13] = [362, 263, 387, 386, 385, 384, 398, 382, 381, 380, 374, 373, 466];

fn euclidean(a: [f64; 2], b: [f64; 2]) -> f64 {
    ((a[0] - b[0]).powi(2) + (a[1] - b[1]).powi(2)).sqrt()
}

/// 60-feature keypoint vector whose values shift with the normalized gaze position (nx, ny).
/// This mirrors the flattened keypoints the tracker produces from eye landmarks.
fn keypoints_for(nx: f64, ny: f64) -> Vec<f64> {
    let mut v = Vec::with_capacity(60);
    for i in 0..27 {
        v.push(0.4 + 0.15 * nx + 0.01 * (i as f64 % 9.0));
        v.push(0.4 + 0.15 * ny + 0.01 * (i as f64 / 9.0));
    }
    v.extend_from_slice(&[1.0, 1.0, 100.0, 100.0, 0.0, 0.0]);
    v
}

/// 478 landmarks with a fixed face bounding box; the eye landmarks shift with gaze.
fn landmarks_for(nx: f64, ny: f64) -> Vec<[f64; 2]> {
    let mut lm = vec![[0.5, 0.5]; 478];
    // Two anchors pin the bounding box to a large, fixed region.
    lm[0] = [0.2, 0.2];
    lm[1] = [0.8, 0.8];
    for i in 2..478 {
        lm[i] = [
            0.3 + 0.3 * ((i % 30) as f64 / 29.0),
            0.3 + 0.3 * ((i / 30) as f64 / 15.0),
        ];
    }
    // Emulate the iris moving toward the gaze point (stays inside the box).
    for &idx in LEFT_EYE.iter().chain(RIGHT_EYE.iter()) {
        lm[idx][0] += 0.05 * nx;
        lm[idx][1] += 0.05 * ny;
    }
    lm
}

fn now_zero() -> f64 {
    0.0
}

#[test]
fn calibrator_predictions_track_synthetic_targets() {
    let mut c = Calibrator::new();

    // Point 0: top-left.
    for _ in 0..30 {
        c.add(keypoints_for(0.25, 0.25), [0.25 * SCREEN_W, 0.25 * SCREEN_H]);
    }
    let p0 = c.predict(&keypoints_for(0.25, 0.25));
    assert!(p0[0].is_finite() && p0[1].is_finite(), "non-finite prediction: {p0:?}");
    let target0 = [0.25 * SCREEN_W, 0.25 * SCREEN_H];
    let target1 = [0.5 * SCREEN_W, 0.75 * SCREEN_H];
    assert!(
        euclidean(p0, target0) < euclidean(p0, target1),
        "point 0 not nearest its own target: {p0:?}"
    );

    c.next_point();

    // Point 1: center-bottom.
    for _ in 0..30 {
        c.add(keypoints_for(0.5, 0.75), target1);
    }
    let p1 = c.predict(&keypoints_for(0.5, 0.75));
    assert!(p1[0].is_finite() && p1[1].is_finite(), "non-finite prediction: {p1:?}");
    assert!(
        euclidean(p1, target1) < euclidean(p1, target0),
        "point 1 not nearest its own target: {p1:?}"
    );

    // Predictions must not blow up to screen-edge/saturation values.
    assert!(p1[0].abs() < 10.0 * SCREEN_W && p1[1].abs() < 10.0 * SCREEN_H, "saturated: {p1:?}");
}

#[test]
fn v5_full_calibration_completes_without_crashing() {
    // sampling_fps = 0.0 -> one calibration sample per frame, no real clock needed.
    // dynamic_recalib = false so the tracker doesn't ask for more points after finishing.
    let mut core = EyeGesturesCoreV5::new_with_clock(SCREEN_W, SCREEN_H, false, 0.0, now_zero);

    let mut result = None;
    for _ in 0..1500 {
        let cp = core.calibrator.current_point(SCREEN_W, SCREEN_H);
        let nx = cp[0] / SCREEN_W;
        let ny = cp[1] / SCREEN_H;
        let lm = landmarks_for(nx, ny);
        result = Some(core.process_landmarks(&lm));

        if !result.as_ref().unwrap().calibrating {
            break;
        }
    }

    let r = result.expect("at least one frame was processed");
    assert!(r.x.is_finite() && r.y.is_finite(), "non-finite gaze: ({}, {})", r.x, r.y);
    assert!(r.x >= 0.0 && r.x <= SCREEN_W, "x out of bounds: {}", r.x);
    assert!(r.y >= 0.0 && r.y <= SCREEN_H, "y out of bounds: {}", r.y);
    assert!(core.samples_taken > 0, "no samples were taken");

    // Calibration must sweep through every point and finish (no deadlock on a stuck point).
    assert!(
        !r.calibrating,
        "calibration did not finish: counter = {}/{}",
        core.calib_counter,
        core.calib_max
    );
    assert_eq!(core.calib_counter, 25, "expected all 25 calibration points to complete");
}
