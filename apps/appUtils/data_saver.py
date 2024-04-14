
import pickle
import csv
import os

def save_gaze_data_to_csv(filename, gevent,rois_to_save):
    """Saves gaze event data from a Gevent object to a CSV file,
       extracting relevant data during saving.

    Args:
        filename (str): Name of the CSV file to save data to.
        gevent (Gevent): The Gevent object containing gaze event data.
        append (bool, optional): If True, appends data to an existing file. Defaults to False.
    """

    headers = ["point_x", "point_y", "blink", "fixation", "screen_x", "screen_y",
               "l_eye_landmarks", "r_eye_landmarks", "l_eye_pupil", "r_eye_pupil",
               "screen_width", "screen_height","rois"]
    write_headers = not os.path.exists(filename)
    append = os.path.exists(filename)

    with open(filename, 'a' if append else 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_headers:
            writer.writerow(headers)

        # Extract data during saving
        point_x, point_y = gevent.point
        screen_x, screen_y = gevent.point_screen
        l_eye_landmarks = gevent.l_eye.getLandmarks()  # Assuming get_landmarks() returns landmarks
        r_eye_landmarks = gevent.r_eye.getLandmarks()  # Assuming get_landmarks() returns landmarks
        l_eye_pupil = gevent.l_eye.getPupil()        # Assuming get_pupils() returns pupils
        r_eye_pupil = gevent.r_eye.getPupil()        # Assuming get_pupils() returns pupils
        screen_width = gevent.screen_man.width
        screen_height = gevent.screen_man.height

        row = [point_x, point_y, gevent.blink, gevent.fixation,
               screen_x, screen_y,
               pickle.dumps(l_eye_landmarks),
               pickle.dumps(r_eye_landmarks),
               pickle.dumps(l_eye_pupil),
               pickle.dumps(r_eye_pupil),
               screen_width, screen_height, rois_to_save]

        writer.writerow(row)
