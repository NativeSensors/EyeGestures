use crate::eyegestures::EyeGesturesCore;
use pyo3::prelude::*;

#[pyclass]
pub struct EyeGesturesEnginePython{
    core: EyeGesturesCore,
}

#[pymethods]
impl EyeGesturesEnginePython {
    #[new]
    pub fn new(screen_width: f64, screen_height: f64) -> Self {
        Self{
            core: EyeGesturesCore::new(screen_width, screen_height),
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

    /// Manually add a calibration point at (x, y)
    pub fn add_calibration_point(&mut self, x: f64, y: f64) {
        self.core.add_calibration_point(x, y);
    }

    /// Reset calibration state
    pub fn recalibrate(&mut self) {
        self.core.recalibrate();
    }

    /// Get current calibration counter
    #[getter]
    pub fn calib_counter(&self) -> usize {
        self.core.calib_counter
    }

    /// Get current calibration max
    #[getter]
    pub fn calib_max(&self) -> usize {
        self.core.calib_max
    }
}
