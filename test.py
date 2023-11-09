import matplotlib.pyplot  as plt
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import time 
import math

points = np.array([(0.95,0.95),
                             (0.05,0.05),
                             (0.95,0.05),
                             (0.05,0.95),
                             (0.5,0.95),
                             (0.5,0.05),
                             (0.95,0.5),
                             (0.5,0.5),
                             (0.05,0.5)])

interpolated = []
step = 0.01
for n,point in enumerate(points):
    if n+1 >= len(points):
        break
    
    print("==============================================================================================")
    next_point = points[n+1].copy()
    print(f"{next_point[0] - point[0]}, {next_point}, {point}")

    dir_x = math.ceil((next_point[0] - point[0])/abs(next_point[0] - point[0]+0.000001))
    dir_y = math.ceil((next_point[1] - point[1])/abs(next_point[1] - point[1]+0.000001))
    
    print(f"int: {dir_x} float: {(next_point[1] - point[1])/abs(next_point[1] - point[1]+0.000001)}")
    print(f"int: {dir_y} float: {(next_point[1] - point[1])/abs(next_point[1] - point[1]+0.000001)}")
    interpolated.append(point)
    
    new_point = point.copy()
    while np.linalg.norm(new_point-next_point) > 0.01 and 1.0 > new_point[0] > 0 and 1.0 > new_point[1] > 0:
        new_point[0] = new_point[0] + dir_x * step
        new_point[1] = new_point[1] + dir_y * step
        
        interpolated.append(new_point.copy())

    
print(point,next_point,dir_x,dir_y)

interpolated = np.array(interpolated)

plt.scatter(interpolated[:,0],interpolated[:,1])
plt.show()

