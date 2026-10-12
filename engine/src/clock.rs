/// Clock returning monotonic milliseconds. A plain fn pointer (not a closure) keeps
/// `EyeGesturesCore` `Send + Sync`, which pyo3 requires for `#[pyclass]`.
/// Tests inject their own clock via `EyeGesturesCore::new_with_clock`.
pub type NowFn = fn() -> f64;

/// Default sampling frequency of the calibration data acquisition, in samples per second.
pub fn default_sampling_fps() -> f64 {
    30.0
}

/// `std::time::Instant` is unsupported on `wasm32-unknown-unknown` and panics at runtime,
/// so browsers get `Date.now()` instead. `Date.now()` is wall-clock time, therefore callers
/// must clamp negative deltas (see `EyeGesturesCore::process_landmarks`).
#[cfg(all(target_arch = "wasm32", feature = "wasm"))]
pub fn default_now_ms() -> f64 {
    js_sys::Date::now()
}

#[cfg(not(all(target_arch = "wasm32", feature = "wasm")))]
pub fn default_now_ms() -> f64 {
    use std::sync::OnceLock;
    use std::time::Instant;

    static START: OnceLock<Instant> = OnceLock::new();
    START.get_or_init(Instant::now).elapsed().as_secs_f64() * 1000.0
}

pub fn system_clock() -> NowFn {
    default_now_ms
}

/// Convert a sampling frequency to a sampling interval in milliseconds.
/// Anything `<= 0` disables the cap (`0.0`, i.e. sample on every frame).
pub fn interval_from_fps(sampling_fps: f64) -> f64 {
    if sampling_fps > 0.0 {
        1000.0 / sampling_fps
    } else {
        0.0
    }
}
