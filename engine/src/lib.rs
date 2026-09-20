pub mod clock;
mod calibrator;
mod fixation;
mod eyegestures;

#[cfg(target_arch = "wasm32")]
pub mod wasm;

#[cfg(feature = "python")]
pub mod python;

#[cfg(feature = "python")]
use pyo3::prelude::*;

pub use calibrator::Calibrator;
pub use fixation::Fixation;
pub use eyegestures::EyeGesturesCore;
pub use clock::{default_now_ms, system_clock, NowFn, DEFAULT_SAMPLING_FPS};

#[cfg(feature = "python")]
#[pymodule]
#[pyo3(name = "EyegesturesEngine")]
fn eyegestures_engine(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<python::EyeGesturesEnginePython>()?;
    Ok(())
}

pub fn euclidean_distance(a: &[f64], b: &[f64]) -> f64 {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| (x - y).powi(2))
        .sum::<f64>()
        .sqrt()
}
