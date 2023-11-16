import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# Provided points
points = np.array([
    [1, 2], [2, 4], [4, 3], [5, 1], [4, -1], [2, -2]
])

# Function to fit a quadratic curve and find intersections
def fit_curve(p1, p2):
    # Fit a quadratic curve (ax^2 + bx + c) through the points
    coefficients = np.polyfit([p1[0], p2[0]], [p1[1], p2[1]], 2)
    curve = np.poly1d(coefficients)

    return curve

# Function to find intersections with y = 0
def find_intersections(curve, points):
    def intersection(x):
        return curve(x)

    intersection_points = fsolve(intersection, 0)
    return (intersection_points,0)

def getCurves(points, reference_point):
    segments = []
    intersection_points = []
    for i in range(len(points)):
        p1, p2 = points[i], points[(i + 1 ) % len(points)]
        if (p1[1] - reference_point[1]) * (p2[1] - reference_point[1]) < 0:
            curve = fit_curve(p1, p2)
            
            segment_x_range = np.linspace(p1[0], p2[0], 100)
            segments.append((curve,segment_x_range))
            x = find_intersections(curve,np.array([p1, p2]))
            intersection_points.append(x)

    return segments,intersection_points

segments, intersections = getCurves(points,[0,0])
# Plotting the pseudo-elliptic shape
x_range = np.linspace(min(points[:, 0]), max(points[:, 0]), 400)
plt.scatter(points[:, 0], points[:, 1], color='red', label="Points")
plt.axhline(0, color='green', linestyle='--', label="y=0 Line")

# Fit curves and find intersections
for n,(segment,intersection) in enumerate(zip(segments, intersections)):
    
    curve, segment_x_range = segment
    plt.plot(segment_x_range, curve(segment_x_range), label=f"Segment {n+1}")
    plt.scatter(intersection[0], intersection[1], color='blue', label=f"Intersection {n+1}")


# plt.scatter(all_intersections)
plt.legend()
plt.show()

