// Reservoir Computing module for processing sequential facial landmarks.
use ndarray::{Array1, Array2, ArrayView1};
use ndarray_rand::RandomExt;
use rand::distributions::Uniform;

#[derive(Clone)]
pub struct Reservoir {
    weights_input: Array2<f64>,
    weights_reservoir: Array2<f64>,
    state: Array1<f64>,
    leak_rate: f64,
    input_size: usize,
}

impl Reservoir {
    /// Initialize a new reservoir with given dimensions.
    /// 
    /// # Arguments
    /// * `input_size` - Number of input features (e.g., flattened landmarks).
    /// * `reservoir_size` - Number of neurons in the reservoir.
    /// * `leak_rate` - Leak rate for the reservoir state update (0.0 to 1.0).
    pub fn new(input_size: usize, reservoir_size: usize, leak_rate: f64) -> Self {
        // Initialize input weights randomly between -0.5 and 0.5
        let weights_input = Array2::random((reservoir_size, input_size), Uniform::new(-0.5, 0.5));
        
        // Initialize reservoir weights with sparsity (90% zeros)
        let mut weights_reservoir = Array2::random((reservoir_size, reservoir_size), Uniform::new(-0.5, 0.5));
        weights_reservoir.map_inplace(|x| {
            if rand::random::<f64>() < 0.9 {
                *x = 0.0; // 90% sparsity
            }
        });
        
        // Scale reservoir weights so their spectral radius matches the target. A spectral
        // radius below 1 is what guarantees the echo state property (stable, fading memory).
        let target_spectral_radius = 0.9;
        let radius = spectral_radius(&weights_reservoir, 100);
        if radius > 0.0 {
            weights_reservoir.mapv_inplace(|x| x * target_spectral_radius / radius);
        }
        
        Self {
            weights_input,
            weights_reservoir,
            state: Array1::zeros(reservoir_size),
            leak_rate,
            input_size,
        }
    }
    
    /// Update the reservoir state with a new input.
    /// 
    /// # Arguments
    /// * `input` - Input vector (e.g., flattened landmarks).
    pub fn update(&mut self, input: ArrayView1<f64>) {
        // Leaky-integrator echo state network. The nonlinearity is applied *before* the
        // leaky blend, which keeps the state bounded in (-1, 1) and is what makes the
        // reservoir a nonlinear feature extractor rather than an unbounded linear filter.
        let pre_activation: Array1<f64> = self.weights_reservoir.dot(&self.state)
            + self.weights_input.dot(&input);
        let activated = pre_activation.mapv(|x| x.tanh());
        
        self.state = self.state.mapv(|x| x * (1.0 - self.leak_rate))
            + activated.mapv(|x| x * self.leak_rate);
    }
    
    /// Get the current reservoir state.
    pub fn get_state(&self) -> Array1<f64> {
        self.state.clone()
    }
    
    /// Reset the reservoir state.
    pub fn reset(&mut self) {
        self.state.fill(0.0);
    }
    
    /// Get the input size (number of features expected by the reservoir).
    pub fn input_size(&self) -> usize {
        self.input_size
    }
    
    /// Clone the reservoir (deep copy of weights and state).
    pub fn clone(&self) -> Self {
        Self {
            weights_input: self.weights_input.clone(),
            weights_reservoir: self.weights_reservoir.clone(),
            state: self.state.clone(),
            leak_rate: self.leak_rate,
            input_size: self.input_size,
        }
    }
}

/// Estimate the spectral radius (largest absolute eigenvalue) of `matrix` via power iteration.
/// Returns 0.0 for a zero/empty matrix, in which case no rescaling happens.
fn spectral_radius(matrix: &Array2<f64>, iterations: usize) -> f64 {
    let n = matrix.ncols();
    if n == 0 {
        return 0.0;
    }

    let mut v = Array1::from_elem(n, 1.0 / (n as f64).sqrt());
    for _ in 0..iterations {
        let av = matrix.dot(&v);
        let norm = av.dot(&av).sqrt();
        if norm <= 0.0 {
            return 0.0;
        }
        v = av / norm;
    }

    let av = matrix.dot(&v);
    (av.dot(&v) / v.dot(&v)).abs()
}