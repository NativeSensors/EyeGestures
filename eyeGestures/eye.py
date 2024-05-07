"""Module providing a extraction of eye from face object."""

import cv2
import numpy as np
import mediapipe as mp


class Eye:
    """Class storing data related and representing a eye"""
    LEFT_EYE_KEYPOINTS = np.array(
        list(mp.solutions.face_mesh.FACEMESH_LEFT_EYE))[:, 0]
    RIGHT_EYE_KEYPOINTS = np.array(
        list(mp.solutions.face_mesh.FACEMESH_RIGHT_EYE))[:, 0]
    LEFT_EYE_IRIS_KEYPOINT = []
    RIGHT_EYE_IRIS_KEYPOINT = []
    LEFT_EYE_PUPIL_KEYPOINT = [473]
    RIGHT_EYE_PUPIL_KEYPOINT = [468]

    # LEFT_EYE_KEYPOINTS = [36, 37, 38, 39, 40, 41] # keypoint indices for left eye
    # RIGHT_EYE_KEYPOINTS = [42, 43, 44, 45, 46, 47] # keypoint indices for right eye

    scale = (150, 100)

    def __init__(self, side: int):

        # check if eye is left or right
        if side == 1:
            self.side = "right"
            self.pupil_index = self.RIGHT_EYE_PUPIL_KEYPOINT
        elif side == 0:
            self.side = "left"
            self.pupil_index = self.LEFT_EYE_PUPIL_KEYPOINT

        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.center_x = 0
        self.center_y = 0
        self.image = None
        self.pupil = None
        self.offset = None
        self.region = None
        self.cut_image = None
        self.landmarks = None

        # self._process(self.image,self.region)

    def update(self, image: np.ndarray, landmarks: list, offset: np.ndarray):
        """function updating data stored inside eye object"""

        self.image = image
        self.offset = offset
        self.landmarks = landmarks

        # check if eye is left or right
        if self.side == "right":
            self.region = np.array(
                landmarks[self.RIGHT_EYE_KEYPOINTS], dtype=np.int32)

        elif self.side == "left":
            self.region = np.array(
                landmarks[self.LEFT_EYE_KEYPOINTS], dtype=np.int32)

        self.pupil = landmarks[self.pupil_index][0]
        self._process(self.image, self.region)

    def getCenter(self):
        """function returning center of eye"""

        return (self.center_x, self.center_y)

    def getPos(self):
        """function returning position of eye in the image"""

        return (self.x, self.y)

    def getPupil(self):
        """function returning pupil object"""

        # return self.pupil.getCoords()
        return self.pupil

    def getBlink(self):
        """function returning blink event"""
        # return self.pupil.getCoords()
        return (self.height) <= 3  # 2x margin

    def getImage(self):
        """function returning image of the eye cut from the entire face image"""

        # TODO: draw additional parameters
        return self.cut_image

    def getGaze(self, gaze_buffor, y_correction=0, x_correction=0):
        """function returning gaze position"""

        # pupilCoords = self.pupil.getCoords()
        center = np.array((self.center_x, self.center_y)) - self.offset

        region_corrected = self.region - self.offset
        pupil_corrected = self.pupil - self.offset

        vectors = region_corrected - center
        pupil = pupil_corrected - center

        vectors = vectors - pupil
        gaze_vector = np.zeros((2))

        gaze_vector[1] = np.sum(vectors, axis=0)[1] * 10 - y_correction
        gaze_vector[0] = -np.sum(vectors, axis=0)[0] * 10 - x_correction

        # print("gaze_vector: ",gaze_vector)
        gaze_buffor.add(gaze_vector)
        return gaze_buffor.getAvg()

    def getOpenness(self):
        """function returning eye openness"""

        return self.height/2

    def getLandmarks(self):
        """function returning eye landmarks"""

        return self.region
    
    def getBoundingBox(self):
        return (self.x,self.y,self.width,self.height)

    def _process(self, image, region):
        h, w, _ = image.shape

        mask = np.full((h, w), 0, dtype=np.uint8)
        background = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [region], 0)

        masked_image = cv2.bitwise_not(background, cv2.cvtColor(
            image.copy(), cv2.COLOR_BGR2GRAY), mask=mask)

        margin = 2
        min_x = np.min(region[:, 0]) - margin
        max_x = np.max(region[:, 0]) + margin
        min_y = np.min(region[:, 1]) - margin
        max_y = np.max(region[:, 1]) + margin

        self.x = min_x
        self.y = min_y

        self.width = np.max(region[:, 0]) - np.min(region[:, 0])
        self.height = np.max(region[:, 1]) - np.min(region[:, 1])

        self.center_x = (min_x + max_x)/2
        self.center_y = (min_y + max_y)/2

        # HACKETY_HACK:
        self.pupil[1] = np.min(region[:, 1])

        self.cut_image = masked_image[min_y:max_y, min_x:max_x]
        # print(f"here: {self.cut_image.shape,min_y,max_y,min_x,max_x}")
        self.cut_image = cv2.cvtColor(self.cut_image, cv2.COLOR_GRAY2BGR)

        for point in self.region:
            point = point - (min_x, min_y)
            cv2.circle(self.cut_image, point.astype(
                int), 1, (255, 0, 0, 150), 1)

        pupil = self.pupil - (min_x, min_y)

        # print(f"pupil: {pupil}")
        cv2.circle(self.cut_image, pupil.astype(int), 1, (0, 255, 0, 150), 1)

        self.cut_image = cv2.resize(self.cut_image, self.scale)

        # save cut_image to buffor and get avg from previous buffors
        # self.eyeBuffer.add(self.cut_image)
        # self.cut_image = np.array(self.eyeBuffer.getAvg(), dtype=np.uint8)

        # LEGACY
        # org_scale = (max_x - min_x,max_y - min_y)
        # self.pupil = pupil.Pupil(self.cut_image, min_x, min_y, self.scale, org_scale)
