import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Set the backend to TkAgg
import matplotlib.pyplot as plt


points = np.array([[222, 133],
                   [200, 130],
                   [201, 129],
                   [210, 127],
                   [207, 134],
                   [225, 131],
                   [216, 127],
                   [204, 133],
                   [217, 134],
                   [202, 131],
                   [203, 128],
                   [221, 129],
                   [200, 130],
                   [206, 128],
                   [212, 135],
                   [225, 133]])

min_x = np.min(points[:,0]) 
max_x = np.max(points[:,0]) 
min_y = np.min(points[:,1]) 
max_y = np.max(points[:,1]) 

center = np.array(((max_x+min_x)/2,(max_y+min_y)/2))
# print(min_x,max_x,center)

points = points - center
center = center - center

# Function to generate random points on an ellipse
def generate_ellipse_points(center, a, b, n=20):
    angles = np.linspace(0, 2 * np.pi, n)
    return np.array([[center[0] + a * np.cos(angle), center[1] + b * np.sin(angle)] for angle in angles])

# Function to calculate the corrected gaze vector
def calculate_corrected_gaze_vector(random_point, points):
    vectors = points - random_point
    # print(vectors)
    distances = np.linalg.norm(vectors, axis=1)
    # print(distances)
    weights = np.exp(-distances)  # Exponential weighting based on distance
    # print(weights)
    weighted_vectors = vectors * weights[:, None]
    gaze_vector = np.sum(weighted_vectors, axis=0) 
    # print(gaze_vector/1000)
    return gaze_vector * 100

# Function to check if a point is inside the ellipse
def is_point_inside_ellipse(point, center, a, b):
    # Adjust point based on the center of ellipse
    px, py = point[0] - center[0], point[1] - center[1]
    # Check the ellipse equation (x^2/a^2 + y^2/b^2 <= 1)
    return (px**2) / (a**2) + (py**2) / (b**2) <= 1

def calculate_vector(random_point, a, b):

    # Example ellipse parameters
    # center = np.array([0, 0])

    # Generate points on the ellipse
    # points = generate_ellipse_points(center, a, b)

    # Generate a random point inside the ellipse


    # Calculate the gaze vector
    gaze_vector = calculate_corrected_gaze_vector(random_point, points)

    
    # Normalize and extend the gaze vector for better visibility
    gaze_vector_normalized = gaze_vector / np.linalg.norm(gaze_vector)
    gaze_vector_extended = gaze_vector_normalized

    return gaze_vector_extended

# Plotting
fig, ax = plt.subplots()

a, b = 5, 3  # Semi-major and semi-minor axes of the ellipse
# Example ellipse parameters
# center = np.array([0, 0])

# Generate points on the ellipse
# points = generate_ellipse_points(center, a, b)
random_point = center


plt.scatter(points[:, 0], points[:, 1], color='blue', label='Elliptic Points')
point, = ax.plot(random_point[0], random_point[1], color='orange', label='Random Point')
r_vector, = ax.plot([0], [0], 'g-')

# Event handler to update the point position
def on_move(event):
    if event.inaxes == ax:

        a, b = 5, 3  # Semi-major and semi-minor axes of the ellipse
        random_point = np.array([event.xdata,event.ydata])

        gaze_vector_extended = calculate_vector(random_point,a,b)

        point.set_data(random_point[0], random_point[1])
        r_vector.set_data([random_point[0], random_point[0] + gaze_vector_extended[0]], 
                                  [random_point[1], random_point[1] + gaze_vector_extended[1]])


        fig.canvas.draw()


# Connect the event handler to the figure
fig.canvas.mpl_connect('motion_notify_event', on_move)

plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.gca().set_aspect('equal', adjustable='box')
plt.title("Corrected Gaze Vector Calculation")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()
plt.grid(True)
plt.show()
