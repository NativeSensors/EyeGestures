use crate::eyegestures_v5::EyeGesturesCoreV5;
use pyo3::prelude::*;

#[pyclass]
pub struct EyeGesturesEnginePythonV5 {
    core: EyeGesturesCoreV5,
}

#[pymethods]
impl EyeGesturesEnginePythonV5 {
    #[new]
    pub fn new(screen_width: f64, screen_height: f64, dynamic_recalib: bool) -> Self {
        Self {
            core: EyeGesturesCoreV5::new(screen_width, screen_height, dynamic_recalib),
        }
    }

    /// Process landmarks and return [x, y, calibrating, calib_x, calib_y]
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

    /// Reset calibration state
    pub fn recalibrate(&mut self) {
        self.core.recalibrate();
    }

    /// Adjust reservoir parameters.
    /// 
    /// # Arguments
    /// * `reservoir_size` - Number of neurons in the reservoir.
    /// * `leak_rate` - Leak rate for the reservoir state update (0.0 to 1.0).
    pub fn set_reservoir_params(&mut self, reservoir_size: usize, leak_rate: f64) {
        self.core.set_reservoir_params(reservoir_size, leak_rate);
    }
}