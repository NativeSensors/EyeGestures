import eyeGestures.screenTracker.dataPoints as dp
import eyeGestures.screenTracker.screenTracker as scrtr

# virtual tracking ScreenProcessor
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

# region of interest inside the virtual ScreenProcessor
ROI_WIDTH = 50
ROI_HEIGHT = 50

# size of real display
DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 1800

####################### ScreenProcessor 2 display Tests #################################


def test_screen2display_1_1():
    """[TEST]"""
    point = (1, 1)

    roi = dp.ScreenROI(0, 0, ROI_WIDTH, ROI_HEIGHT)
    display = dp.Display(DISPLAY_WIDTH, DISPLAY_HEIGHT, 0, 0)

    tracker = scrtr.ScreenProcessor()
    p = tracker.screen2display(point, roi, display)

    assert p == (point[0]/ROI_WIDTH * DISPLAY_WIDTH,
                 point[1]/ROI_HEIGHT * DISPLAY_HEIGHT)


def test_screen2display_55_1():
    """[TEST]"""
    point = (55, 1)

    roi = dp.ScreenROI(0, 0, ROI_WIDTH, ROI_HEIGHT)
    display = dp.Display(DISPLAY_WIDTH, DISPLAY_HEIGHT, 0, 0)

    tracker = scrtr.ScreenProcessor()
    p = tracker.screen2display(point, roi, display)

    assert p == (DISPLAY_WIDTH,
                 point[1]/ROI_HEIGHT * DISPLAY_HEIGHT)


def test_screen2display_55_55():
    """[TEST]"""
    point = (55, 55)

    roi = dp.ScreenROI(0, 0, ROI_WIDTH, ROI_HEIGHT)
    display = dp.Display(DISPLAY_WIDTH, DISPLAY_HEIGHT, 0, 0)

    tracker = scrtr.ScreenProcessor()
    p = tracker.screen2display(point, roi, display)

    assert p == (DISPLAY_WIDTH,
                 DISPLAY_HEIGHT)


def test_screen2display_0_0():
    """[TEST]"""
    point = (0, 0)

    roi = dp.ScreenROI(0, 0, ROI_WIDTH, ROI_HEIGHT)
    display = dp.Display(DISPLAY_WIDTH, DISPLAY_HEIGHT, 0, 0)

    tracker = scrtr.ScreenProcessor()
    p = tracker.screen2display(point, roi, display)

    assert p == (0, 0)


def test_screen2display_1_1_pos_50_50():
    """[TEST]"""
    point = (51, 51)
    pos = (50, 50)

    roi = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH, ROI_HEIGHT)
    display = dp.Display(DISPLAY_WIDTH, DISPLAY_HEIGHT, 0, 0)

    tracker = scrtr.ScreenProcessor()
    p = tracker.screen2display(point, roi, display)

    assert p == ((point[0] - pos[0])/ROI_WIDTH * DISPLAY_WIDTH,
                 (point[1] - pos[1])/ROI_HEIGHT * DISPLAY_HEIGHT)


def test_screen2display_55_55_pos_50_50():
    """[TEST]"""
    point = (105, 105)
    pos = (50, 50)

    roi = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH, ROI_HEIGHT)
    display = dp.Display(DISPLAY_WIDTH, DISPLAY_HEIGHT, 0, 0)

    tracker = scrtr.ScreenProcessor()
    p = tracker.screen2display(point, roi, display)

    assert p == (DISPLAY_WIDTH,
                 DISPLAY_HEIGHT)


def test_screen2display_0_0_pos_50_50():
    """[TEST]"""
    point = (0, 0)
    pos = (50, 50)

    roi = dp.ScreenROI(pos[0], pos[1], ROI_WIDTH, ROI_HEIGHT)
    display = dp.Display(DISPLAY_WIDTH, DISPLAY_HEIGHT, 0, 0)

    tracker = scrtr.ScreenProcessor()
    p = tracker.screen2display(point, roi, display)

    assert p == (0, 0)
