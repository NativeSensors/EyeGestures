use std::collections::VecDeque;

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
        // Match JS MLR behavior: include a bias/intercept feature.
        let mut x_with_bias = x;
        x_with_bias.push(1.0);
        self.x_data.push(x_with_bias);
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

        for (i, row) in xtx.iter_mut().enumerate() {
            row[i] += 1e-9;
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
    tmp_x: VecDeque<Vec<f64>>,
    stable_x: Vec<Vec<f64>>,
    tmp_y: VecDeque<[f64; 2]>,
    stable_y: Vec<[f64; 2]>,
    reg_x: LinearRegression,
    reg_y: LinearRegression,
    point_index: usize,
    pub fitted: bool,
}

impl Calibrator {
    pub fn new() -> Self {
        Self {
            tmp_x: VecDeque::new(),
            stable_x: vec![],
            tmp_y: VecDeque::new(),
            stable_y: vec![],
            reg_x: LinearRegression::new(),
            reg_y: LinearRegression::new(),
            point_index: 0,
            fitted: false,
        }
    }

    pub fn add(&mut self, keypoints: Vec<f64>, target: [f64; 2]) {
        self.tmp_x.push_back(keypoints);
        self.tmp_y.push_back(target);

        if self.tmp_x.len() > 40 {
            self.tmp_x.pop_front();
            self.tmp_y.pop_front();
        }

        let all_x: Vec<Vec<f64>> = self.tmp_x.iter().chain(self.stable_x.iter()).cloned().collect();
        let all_y: Vec<[f64; 2]> = self.tmp_y.iter().chain(self.stable_y.iter()).cloned().collect();

        self.reg_x = LinearRegression::new();
        self.reg_y = LinearRegression::new();
        for (x, y) in all_x.into_iter().zip(all_y.into_iter()) {
            self.reg_x.add_sample(x.clone(), y[0]);
            self.reg_y.add_sample(x, y[1]);
        }

        self.reg_x.fit();
        self.reg_y.fit();

        self.fitted = self.reg_x.fitted && self.reg_y.fitted;
    }

    pub fn predict(&self, keypoints: &[f64]) -> [f64; 2] {
        if !self.fitted {
            return [0.0, 0.0];
        }
        [self.reg_x.predict(keypoints), self.reg_y.predict(keypoints)]
    }

    pub fn current_point(&self, screen_width: f64, screen_height: f64) -> [f64; 2] {
        let p = CALIB_POINTS[self.point_index];
        [p[0] * screen_width, p[1] * screen_height]
    }

    pub fn next_point(&mut self) {
        let all_x: Vec<Vec<f64>> = self.tmp_x.drain(..).collect();
        let all_y: Vec<[f64; 2]> = self.tmp_y.drain(..).collect();
        self.stable_x.extend(all_x);
        self.stable_y.extend(all_y);
        self.point_index = (self.point_index + 1) % CALIB_POINTS.len();
    }

    pub fn reset(&mut self) {
        *self = Calibrator::new();
    }
}
