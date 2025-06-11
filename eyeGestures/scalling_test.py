import pytest
import eyeGestures.screenTracker.screenTracker as scrtr
import eyeGestures.screenTracker.dataPoints as dp

# region of interest inside the virtual screen
ROI_WIDTH = 30
ROI_HEIGHT = 20

####################### screen 2 display Tests #################################


def test_scaleUpTest():
    pos = (50, 50)
    BIGGER = 10

    roi = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH, ROI_HEIGHT)
    roi2 = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH+BIGGER, ROI_HEIGHT+BIGGER)

    bigger_roi = scrtr.scaleUp(roi, roi2, 0.1)

    assert bigger_roi.width > roi.width
    assert bigger_roi.height > roi.height


def test_scaleUpTest_known():
    pos = (50, 50)
    BIGGER = 10

    roi = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH, ROI_HEIGHT)
    roi2 = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH+BIGGER, ROI_HEIGHT+BIGGER)

    bigger_roi = scrtr.scaleUp(roi, roi2, 0.1)

    assert int(bigger_roi.width) == int(ROI_WIDTH*1.1)
    assert int(bigger_roi.height) == int(ROI_HEIGHT*1.1)


def test_scaleDownTest():
    pos = (50, 50)
    SMALLER = 10

    roi = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH, ROI_HEIGHT)
    roi2 = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH-SMALLER, ROI_HEIGHT-SMALLER)

    smaller_roi = scrtr.scaleDown(roi, roi2, -0.1)

    assert smaller_roi.width < roi.width
    assert smaller_roi.height < roi.height


def test_scaleUpTest_known():
    pos = (50, 50)
    SMALLER = 10

    roi = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH, ROI_HEIGHT)
    roi2 = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH-SMALLER, ROI_HEIGHT-SMALLER)

    smaller_roi = scrtr.scaleDown(roi, roi2, -0.1)

    assert int(smaller_roi.width) == int(ROI_WIDTH*0.9)
    assert int(smaller_roi.height) == int(ROI_HEIGHT*0.9)
