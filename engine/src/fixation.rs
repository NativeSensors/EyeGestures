pub struct Fixation {
    center: [f64; 2],
    radius: f64,
    pub level: f64,
}

impl Fixation {
    pub fn new(x: f64, y: f64, radius: f64) -> Self {
        Self { center: [x, y], radius, level: 0.0 }
    }

    pub fn process(&mut self, x: f64, y: f64) -> f64 {
        let dx = x - self.center[0];
        let dy = y - self.center[1];

        if dx * dx + dy * dy < self.radius * self.radius {
            self.level = (self.level + 0.02).min(1.0);
        } else {
            self.center = [x, y];
            self.level = 0.0;
        }

        self.level
    }
}
