import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle
import csv
import ast
import re
import os

def read_gaze_data_from_csv(filename):
    """Reads gaze event data from a CSV file.

    Args:
        filename (str): Name of the CSV file to read data from.

    Returns:
        list: List of dictionaries containing gaze event data.
    """

    gaze_data = []

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for n,row in enumerate(reader):
            if n > 0:
                # print(n,row[6],type(row[6]),row[6][2])
                # print(bytearray(f'{row[6][2:-3]}', 'latin-1'))
                # Deserialize the string representation of arrays

                row_data = {
                    "timestamp": row[0],
                    "point_x": row[1],
                    "point_y": row[2],
                    "blink": row[3],
                    "fixation": row[4],
                    "screen_x": row[5],
                    "screen_y": row[6],
                    "screen_width": row[7],
                    "screen_height": row[8],
                    "rois": row[12]  # Deserialize the string representation of the array
                }
                gaze_data.append(row_data)

    return gaze_data

def draw_heatmap(data_points,x_dim,y_dim,picture_path = None):
    x_range = [0,x_dim]
    y_range = [0,y_dim]
    heatmap, xedges, yedges = np.histogram2d(data_points[:,0], data_points[:,1], bins = 50, range=[x_range, y_range])
    extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
    alpha = 1.0

    plt.clf()
    if picture_path:
        map_image = plt.imread(picture_path)
        map_image = np.flipud(map_image)
        alpha = 0.5
        plt.imshow(map_image, extent=extent, aspect='auto')


    # Plot the image as background
    plt.imshow(heatmap.T, extent=extent, origin='lower', alpha=alpha, cmap='hot')
    plt.gca().invert_yaxis()
    plt.show()

def main(gaze_data_file,background_file = False, step = None, window_size = None, start = None, stop = None):

    # Example usage:
    # filename = 'data/collection_73cbc017/data.csv'
    # picture = 'data/collection_73cbc017/recordings/1713258117.949606.png'

    # picture = background_file

    recordings_path = f"{os.path.dirname(gaze_data_file)}/recordings"

    filename = gaze_data_file
    gaze_data = read_gaze_data_from_csv(filename)
    data_points = []
    timestamps = []
    screen_w = float(gaze_data[0]["screen_width"])
    screen_h = float(gaze_data[0]["screen_height"])

    for data in gaze_data:
        timestamps.append(float(data["timestamp"]))
        data_points.append([float(data["screen_x"]),float(data["screen_y"])])
    data_points = np.array(data_points)

    if start:
        index = timestamps.index(start)
        timestamps = timestamps[index:]
        data_points = data_points[index:,:]

    if stop:
        index = timestamps.index(stop)
        timestamps = timestamps[:index]
        data_points = data_points[:index,:]

    if window_size == None or step == None:
        picture_path = None
        if background_file:
            picture_path = f"{recordings_path}/{timestamps[0]}.png"
        draw_heatmap(data_points,screen_w,screen_h,picture_path)
    else:
        for i in range(0,len(timestamps),step):
            picture_path = None
            if background_file:
                print(f"{background_file}")
                picture_path = f"{recordings_path}/{timestamps[i]}.png"
            data_points_range = data_points[i:i+window_size]
            draw_heatmap(data_points_range,screen_w,screen_h,picture_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate heatmap based on gaze data over an image.')
    parser.add_argument('path_to_gaze_data', type=str, help='Path to the gaze data file')
    parser.add_argument('--window', type=int, help='Window size in samples')
    parser.add_argument('--step', type=int, help='Window size in samples')
    parser.add_argument('--background',  action='store_true', help='Path to the background file')
    parser.add_argument('--start', type=float, help='Window size in samples')
    parser.add_argument('--stop',  type=float, help='Path to the background file')

    args = parser.parse_args()

    main(args.path_to_gaze_data,background_file = args.background, step = args.step, window_size = args.window, start = args.start, stop = args.stop)
