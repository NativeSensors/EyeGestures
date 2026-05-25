use crate::eyegestures::EyeGesturesCore;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct EyeGesturesEngineWasm{
    core: EyeGesturesCore,
}

#[wasm_bindgen]
impl EyeGesturesEngineWasm {
    #[wasm_bindgen(constructor)]
    pub fn new(screen_width: f64, screen_height: f64) -> Self {
        Self{
            core: EyeGesturesCore::new(screen_width, screen_height),
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

    pub fn add_calibration_point(&mut self, x: f64, y: f64) {
        self.core.add_calibration_point(x, y);
    }

    pub fn recalibrate(&mut self) {
        self.core.recalibrate();
    }
}
