use std::collections::VecDeque;
use ndarray::Array1;

use crate::reservoir::Reservoir;

struct LinearRegression {
    x_data: Vec<Vec<f64>>,
    y_data: Vec<f64>,
    weights: Vec<f64>,
    fitted: bool,
}

impl LinearRegression {
    fn new() -> Self {
        Self { x_data: vec![], y_data: vec![], weights: vec![], fitted: false }
    }

    fn add_sample(&mut self, x: Vec<f64>, y: f64) {
        self.x_data.push(x);
        self.y_data.push(y);
    }

    fn fit(&mut self) {
        let n = self.x_data.len();
        if n == 0 {
            self.fitted = false;
            return;
        }

        let m = self.x_data[0].len();
        let mut xtx = vec![vec![0.0f64; m]; m];
        let mut xty = vec![0.0f64; m];

        for i in 0..n {
            for j in 0..m {
                xty[j] += self.x_data[i][j] * self.y_data[i];
                for k in 0..m {
                    xtx[j][k] += self.x_data[i][j] * self.x_data[i][k];
                }
            }
        }

        // Ridge regularization. Without it, the readout is badly under-determined during the
        // first calibration points (more reservoir features than samples), and the raw least
        // squares solution blows up — pinning predictions to the top/bottom edge of the screen.
        for (i, row) in xtx.iter_mut().enumerate() {
            row[i] += RIDGE_LAMBDA;
        }

        if let Some(w) = gaussian_elimination(xtx, xty) {
            self.weights = w;
            self.fitted = true;
        } else {
            self.fitted = false;
        }
    }

    fn predict(&self, x: &[f64]) -> f64 {
        if !self.fitted {
            return 0.0;
        }
        let weighted_sum: f64 = x.iter().zip(&self.weights).map(|(a, b)| a * b).sum();
        let bias = self.weights.get(x.len()).copied().unwrap_or(0.0);
        weighted_sum + bias
    }
}

/// L2 regularization strength for the readout regression. The reservoir state is bounded in
/// (-1, 1) after the tanh nonlinearity, so this value is a meaningful fraction of the diagonal
/// of `X^T X` (which is on the order of the sample count) and keeps the weights well-behaved.
const RIDGE_LAMBDA: f64 = 1.0;

fn gaussian_elimination(mut a: Vec<Vec<f64>>, mut b: Vec<f64>) -> Option<Vec<f64>> {
    let n = a.len();
    for i in 0..n {
        let max_row = (i..n).max_by(|&r1, &r2| a[r1][i].abs().partial_cmp(&a[r2][i].abs()).unwrap())?;
        a.swap(i, max_row);
        b.swap(i, max_row);

        if a[i][i].abs() < 1e-12 {
            return None;
        }

        for k in i + 1..n {
            let factor = a[k][i] / a[i][i];
            for j in i..n {
                a[k][j] -= factor * a[i][j];
            }
            b[k] -= factor * b[i];
        }
    }

    let mut x = vec![0.0; n];
    for i in (0..n).rev() {
        x[i] = b[i];
        for j in i + 1..n {
            x[i] -= a[i][j] * x[j];
        }
        x[i] /= a[i][i];
    }
    Some(x)
}

const CALIB_POINTS: [[f64; 2]; 25] = [
    [0.25, 0.25], [0.5, 0.75], [1.0, 0.5],  [0.75, 0.5],  [0.0, 0.75],
    [0.5,  0.5],  [1.0, 0.25], [0.75, 0.0], [0.25, 0.5],  [0.5, 0.0],
    [0.0,  0.5],  [1.0, 1.0],  [0.75, 1.0], [0.25, 0.0],  [1.0, 0.0],
    [0.0,  1.0],  [0.25, 1.0], [0.75, 0.75],[0.5, 0.25],  [0.0, 0.25],
    [1.0,  0.5],  [0.75, 0.25],[0.5, 1.0],  [0.25, 0.75], [0.0, 0.0],
];

pub struct Calibrator {
    tmp_states: VecDeque<Vec<f64>>,
    stable_states: Vec<Vec<f64>>,
    tmp_target: VecDeque<[f64; 2]>,
    stable_target: Vec<[f64; 2]>,
    reg_x: LinearRegression,
    reg_y: LinearRegression,
    reservoir: Option<Reservoir>,
    reservoir_size: usize,
    leak_rate: f64,
    point_index: usize,
    pub fitted: bool,
}

impl Calibrator {
    pub fn new() -> Self {
        // The reservoir is created lazily from the first sample: the input size is deduced from
        // the feature count of the first keypoints vector, so the calibrator is agnostic to the
        // upstream feature extraction.
        let reservoir_size = 5;
        let leak_rate = 0.8;

        Self {
            tmp_states: VecDeque::new(),
            stable_states: vec![],
            tmp_target: VecDeque::new(),
            stable_target: vec![],
            reg_x: LinearRegression::new(),
            reg_y: LinearRegression::new(),
            reservoir: None,
            reservoir_size,
            leak_rate,
            point_index: 0,
            fitted: false,
        }
    }

    /// Create the reservoir on the first sample, deducing the input size from the feature count.
    fn ensure_reservoir(&mut self, input_size: usize) {
        if self.reservoir.is_none() {
            self.reservoir = Some(Reservoir::new(input_size, self.reservoir_size, self.leak_rate));
        }
    }

    /// Pad/truncate `keypoints` to exactly the reservoir input size (no-op before the first sample).
    fn fit_input(&self, mut keypoints: Vec<f64>) -> Vec<f64> {
        if let Some(reservoir) = &self.reservoir {
            let input_size = reservoir.input_size();
            if keypoints.len() > input_size {
                keypoints.truncate(input_size);
            } else if keypoints.len() < input_size {
                keypoints.resize(input_size, 0.0);
            }
        }
        keypoints
    }

    pub fn add(&mut self, keypoints: Vec<f64>, target: [f64; 2]) {
        // Deduce the reservoir input size from the first sample.
        self.ensure_reservoir(keypoints.len());

        let keypoints = self.fit_input(keypoints);
        let keypoints_array = Array1::from(keypoints);

        // A single reservoir encodes the keypoints; both readouts share its state.
        self.reservoir.as_mut().unwrap().update(keypoints_array.view());
        self.tmp_states.push_back(self.reservoir.as_ref().unwrap().get_state().to_vec());
        self.tmp_target.push_back(target);

        if self.tmp_states.len() > 40 {
            self.tmp_states.pop_front();
            self.tmp_target.pop_front();
        }

        self.refit();
    }

    fn refit(&mut self) {
        let states: Vec<Vec<f64>> = self.tmp_states.iter().chain(self.stable_states.iter()).cloned().collect();
        let targets: Vec<[f64; 2]> = self.tmp_target.iter().chain(self.stable_target.iter()).copied().collect();

        self.reg_x = LinearRegression::new();
        self.reg_y = LinearRegression::new();
        // Both readouts read the same reservoir state; reg_x predicts the gaze x coordinate and
        // reg_y predicts the gaze y coordinate. `LinearRegression` adds the bias.
        for (state, target) in states.into_iter().zip(targets) {
            self.reg_x.add_sample(state.clone(), target[0]);
            self.reg_y.add_sample(state, target[1]);
        }

        self.reg_x.fit();
        self.reg_y.fit();

        self.fitted = self.reg_x.fitted && self.reg_y.fitted;
    }

    /// Number of samples gathered so far (pending + committed to the stable set).
    pub fn sample_count(&self) -> usize {
        self.tmp_states.len() + self.stable_states.len()
    }

    pub fn predict(&self, keypoints: &[f64]) -> [f64; 2] {
        if !self.fitted {
            return [0.0, 0.0];
        }

        let keypoints = self.fit_input(keypoints.to_vec());
        let keypoints_array = Array1::from(keypoints);

        let mut reservoir = self.reservoir.as_ref().unwrap().clone();
        reservoir.update(keypoints_array.view());
        let state = reservoir.get_state().to_vec();

        [self.reg_x.predict(&state), self.reg_y.predict(&state)]
    }

    pub fn current_point(&self, screen_width: f64, screen_height: f64) -> [f64; 2] {
        let p = CALIB_POINTS[self.point_index];
        [p[0] * screen_width, p[1] * screen_height]
    }

    pub fn next_point(&mut self) {
        let all_states: Vec<Vec<f64>> = self.tmp_states.drain(..).collect();
        let all_targets: Vec<[f64; 2]> = self.tmp_target.drain(..).collect();
        self.stable_states.extend(all_states);
        self.stable_target.extend(all_targets);
        self.point_index = (self.point_index + 1) % CALIB_POINTS.len();
    }

    pub fn reset(&mut self) {
        *self = Calibrator::new();
    }

    /// Adjust reservoir parameters.
    /// 
    /// # Arguments
    /// * `reservoir_size` - Number of neurons in the reservoir.
    /// * `leak_rate` - Leak rate for the reservoir state update (0.0 to 1.0).
    pub fn set_reservoir_params(&mut self, reservoir_size: usize, leak_rate: f64) {
        self.reservoir_size = reservoir_size;
        self.leak_rate = leak_rate;

        if let Some(reservoir) = &self.reservoir {
            let input_size = reservoir.input_size();
            self.reservoir = Some(Reservoir::new(input_size, reservoir_size, leak_rate));
        }
    }
}
