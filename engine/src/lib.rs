pub mod clock;
pub mod reservoir;
mod calibrator;
mod eyegestures;
mod eyegestures_v5;
mod fixation;

#[cfg(target_arch = "wasm32")]
pub mod wasm;

#[cfg(feature = "python")]
pub mod python;

#[cfg(feature = "python")]
use pyo3::prelude::*;

pub use calibrator::Calibrator;
pub use eyegestures::EyeGesturesCore;
pub use eyegestures_v5::EyeGesturesCoreV5;
pub use fixation::Fixation;
pub use clock::{default_now_ms, default_sampling_fps, system_clock, NowFn};

#[cfg(feature = "python")]
pub mod python_v5;

#[cfg(feature = "python")]
#[pymodule]
#[pyo3(name = "EyegesturesEngine")]
fn eyegestures_engine(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<python::EyeGesturesEnginePython>()?;
    module.add_class::<python_v5::EyeGesturesEnginePythonV5>()?;
    Ok(())
}

pub fn euclidean_distance(a: &[f64], b: &[f64]) -> f64 {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| (x - y).powi(2))
        .sum::<f64>()
        .sqrt()
}
