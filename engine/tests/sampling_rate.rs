use std::cell::Cell;

use EyegesturesEngine::{EyeGesturesCore, DEFAULT_SAMPLING_FPS};

thread_local! {
    /// Fake clock shared by all tests; each test runs on its own thread.
    static NOW_MS: Cell<f64> = const { Cell::new(0.0) };
}

fn fake_now_ms() -> f64 {
    NOW_MS.with(|now| now.get())
}

fn advance(ms: f64) {
    NOW_MS.with(|now| now.set(now.get() + ms));
}

/// 478 synthetic face landmarks spread over a small grid (needs index 473 to exist,
/// and a non-degenerate bounding box so width/height are non-zero).
fn landmarks() -> Vec<[f64; 2]> {
    (0..478)
        .map(|i| {
            [
                0.30 + 0.001 * (i % 30) as f64,
                0.30 + 0.001 * (i / 30) as f64,
            ]
        })
        .collect()
}

struct Harness {
    core: EyeGesturesCore,
}

impl Harness {
    fn new(sampling_fps: f64) -> Self {
        NOW_MS.with(|now| now.set(0.0));
        Self {
            core: EyeGesturesCore::new_with_clock(1920.0, 1080.0, true, sampling_fps, fake_now_ms),
        }
    }

    /// Feed `frames` frames at `fps` frames per second, advancing the fake clock.
    fn run(&mut self, frames: usize, fps: f64) {
        let step_ms = 1000.0 / fps;
        for _ in 0..frames {
            advance(step_ms);
            self.core.process_landmarks(&landmarks());
        }
    }

    fn samples(&self) -> usize {
        self.core.samples_taken
    }
}

#[test]
fn default_sampling_rate_is_30hz() {
    let core = EyeGesturesCore::new(1920.0, 1080.0, true);
    assert_eq!(core.sampling_fps(), DEFAULT_SAMPLING_FPS);
}

#[test]
fn high_fps_camera_is_sampled_at_30hz() {
    // 2 seconds of a 120 fps camera -> 240 frames, but only ~60 calibration samples.
    let mut harness = Harness::new(DEFAULT_SAMPLING_FPS);
    harness.run(240, 120.0);
    let samples = harness.samples();
    assert!(
        (58..=62).contains(&samples),
        "expected ~60 samples in 2s at 30Hz, got {samples}"
    );
}

#[test]
fn cap_disabled_samples_every_frame() {
    let mut harness = Harness::new(0.0);
    harness.run(240, 120.0);
    assert_eq!(harness.samples(), 240);
}

#[test]
fn slow_camera_is_unaffected_by_the_cap() {
    // A 30 fps camera samples on every frame, identical to the uncapped behaviour.
    let mut harness = Harness::new(DEFAULT_SAMPLING_FPS);
    harness.run(60, 30.0);
    assert_eq!(harness.samples(), 60);
}

#[test]
fn sampling_rate_is_machine_independent() {
    let mut slow = Harness::new(DEFAULT_SAMPLING_FPS);
    slow.run(60, 30.0);

    let mut fast = Harness::new(DEFAULT_SAMPLING_FPS);
    fast.run(240, 120.0);

    assert_eq!(slow.samples(), 60);
    assert!(
        (58..=62).contains(&fast.samples()),
        "expected ~60 samples, got {}",
        fast.samples()
    );
}

#[test]
fn point_pacing_is_sample_based_not_frame_based() {
    // 40 frames at 120 fps is 1/3 of a second: under the old frame-counted rule that was
    // enough to move to the next point, at 30 Hz it is only ~10 of the 20 required samples
    // (20 samples at 30 Hz take ~667 ms on any machine).
    let mut harness = Harness::new(DEFAULT_SAMPLING_FPS);
    harness.run(40, 120.0);
    let samples = harness.samples();
    assert!(
        (9..=11).contains(&samples),
        "expected ~10 samples after 1/3s, got {samples}"
    );
    assert!(harness.core.samples_on_point < 20);
}

#[test]
fn gaze_tracking_still_runs_on_every_frame() {
    // The cap must only throttle data acquisition: the smoothing buffer (tracker side)
    // keeps filling at the real frame rate.
    let mut harness = Harness::new(DEFAULT_SAMPLING_FPS);
    harness.run(20, 120.0);
    assert_eq!(harness.core.buffer.len(), 20);
    assert!(
        harness.samples() < 20,
        "tracker ran 20 frames, calibration must have sampled fewer"
    );
}

#[test]
fn set_sampling_fps_roundtrip() {
    let mut core = EyeGesturesCore::new(1920.0, 1080.0, true);
    core.set_sampling_fps(60.0);
    assert_eq!(core.sampling_fps(), 60.0);
    core.set_sampling_fps(0.0);
    assert_eq!(core.sampling_fps(), 0.0);
}

#[test]
fn real_clock_samples_at_30hz() {
    // End-to-end check with the actual system clock (not the fake one): feed one second of
    // 240 fps frames and expect ~30 samples regardless of how fast the host runs.
    let mut core = EyeGesturesCore::new(1920.0, 1080.0, true);
    let start = std::time::Instant::now();
    while start.elapsed() < std::time::Duration::from_secs(1) {
        core.process_landmarks(&landmarks());
        std::thread::sleep(std::time::Duration::from_micros(4_000));
    }
    let samples = core.samples_taken;
    // Samples are taken on the first frame at or after each 33.3 ms boundary, so a loaded
    // host (or a slow `process_landmarks`) quantises the rate downwards; allow that slack.
    assert!(
        (20..=40).contains(&samples),
        "expected ~30 samples per second, got {samples}"
    );
}

#[test]
fn recalibrate_resets_the_sampling_clock() {
    let mut harness = Harness::new(DEFAULT_SAMPLING_FPS);
    harness.run(120, 120.0);
    let before = harness.samples();
    harness.core.recalibrate();
    assert_eq!(harness.samples(), 0);
    assert_eq!(harness.core.samples_on_point, 0);
    assert!(before > 0);

    // First frame after a reset samples immediately, no start-up delay.
    harness.run(1, 120.0);
    assert_eq!(harness.samples(), 1);
}
