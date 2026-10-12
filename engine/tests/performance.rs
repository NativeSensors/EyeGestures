// Performance test for EyeGestures V4 vs V5.
use EyegesturesEngine::{EyeGesturesCore, EyeGesturesCoreV5};
use std::time::Instant;

/// Generate synthetic landmarks for testing.
fn generate_landmarks() -> Vec<[f64; 2]> {
    let mut landmarks = vec![[0.0, 0.0]; 468];
    
    // Left eye landmarks (indices 33, 133, 160, 159, 158, 157, 173, 155, 154, 153, 144, 145)
    let left_eye_indices = [33, 133, 160, 159, 158, 157, 173, 155, 154, 153, 144, 145];
    for (i, &idx) in left_eye_indices.iter().enumerate() {
        landmarks[idx] = [0.3 + i as f64 * 0.01, 0.4 + i as f64 * 0.01];
    }
    
    // Right eye landmarks (indices 362, 263, 387, 386, 385, 384, 398, 382, 381, 380, 374, 373)
    let right_eye_indices = [362, 263, 387, 386, 385, 384, 398, 382, 381, 380, 374, 373];
    for (i, &idx) in right_eye_indices.iter().enumerate() {
        landmarks[idx] = [0.6 + i as f64 * 0.01, 0.4 + i as f64 * 0.01];
    }
    
    landmarks
}

/// Test that EyeGestures V5 is not significantly slower than V4.
#[test]
fn test_v5_performance() {
    let landmarks = generate_landmarks();
    let mut v4 = EyeGesturesCore::new(1920.0, 1080.0, true);
    let mut v5 = EyeGesturesCoreV5::new(1920.0, 1080.0, true);
    
    // Warm-up
    for _ in 0..10 {
        v4.process_landmarks(&landmarks);
        v5.process_landmarks(&landmarks);
    }
    
    // Benchmark V4
    let start_v4 = Instant::now();
    for _ in 0..100 {
        v4.process_landmarks(&landmarks);
    }
    let duration_v4 = start_v4.elapsed().as_secs_f64() / 100.0;
    
    // Benchmark V5
    let start_v5 = Instant::now();
    for _ in 0..100 {
        v5.process_landmarks(&landmarks);
    }
    let duration_v5 = start_v5.elapsed().as_secs_f64() / 100.0;
    
    // Allow V5 to be up to 10% slower than V4
    let threshold = duration_v4 * 1.1;
    assert!(duration_v5 <= threshold,
        "EyeGestures V5 is significantly slower than V4: V4={:.6}s, V5={:.6}s",
        duration_v4, duration_v5);
    
    println!("Performance test passed: V4={:.6}s, V5={:.6}s", duration_v4, duration_v5);
}