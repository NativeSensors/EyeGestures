import pickle
import csv
import ast

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
                print(n,row[6],type(row[6]),row[6][2])
                print(bytearray(f'{row[6][2:-3]}', 'latin-1'))
                # Deserialize the string representation of arrays

                row_data = {
                    "point_x": row[0],
                    "point_y": row[1],
                    "blink": row[2],
                    "fixation": row[3],
                    "screen_x": row[4],
                    "screen_y": row[5],
                    "l_eye_landmarks": pickle.loads(bytearray(f'{row[6][2:-1]}', 'latin-1').decode('unicode_escape').encode('latin1')),  # Deserialize the string representation of the array
                    "r_eye_landmarks": pickle.loads(bytearray(f'{row[7][2:-1]}', 'latin-1').decode('unicode_escape').encode('latin1')),  # Deserialize the string representation of the array
                    "l_eye_pupil": pickle.loads(bytearray(f'{row[8][2:-1]}', 'latin-1').decode('unicode_escape').encode('latin1')),  # Deserialize the string representation of the array
                    "r_eye_pupil": pickle.loads(bytearray(f'{row[9][2:-1]}', 'latin-1').decode('unicode_escape').encode('latin1')),  # Deserialize the string representation of the array
                    "screen_width": row[10],
                    "screen_height": row[11],
                    "rois": row[12]  # Deserialize the string representation of the array
                }
                gaze_data.append(row_data)

    return gaze_data

# Example usage:
filename = 'collection_91675a1d.csv'
gaze_data = read_gaze_data_from_csv(filename)
for data in gaze_data:
    print(data)