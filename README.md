## 👁️ EyeGestures

EyeGestures is open source eyetracking software/library using native webcams and phone camers for achieving its goal. The aim of library is to bring accessibility of eyetracking and eyedriven interfaces without requirement of obtaining expensive hardware.

<p align="center">
  <img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/2ad25252-e96e-47d4-b25f-c47ba7f0f4f3" width="300" height="150">
<img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/f3132843-063a-439a-8e1c-2385ddfdccda" width="300
" height="150">
</p>

### ⭐ Mission 

There is no one size-fits all solution, and we believe that differentiating interfaces brings accessibility to digital spaces. Designing eye-driven interfaces gives more control over computers to those who cannot fully enjoy their capabilities due to different disabilities, as well as an additional way to control your computer for rests. 

Such technology should not be paywalled by expensive eye-tracking hardware, especially in case when it is needed to exist in the digital world and operate your computer. Most of the current consumer electronics devices have built-in native cameras, and the current state of research indicates that it is achievable to have eye tracking at reasonable accuracy based on those native cameras. 

Our mission is to bring eye-tracking technology to as many people as possible. 

Our technology is not perfect, but we strive to be.

### 📢 Announcements:

<a href="https://polar.sh/NativeSensors/posts"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/posts.svg?org=NativeSensors&darkmode"><img alt="Posts on Polar" src="https://polar.sh/embed/posts.svg?org=NativeSensors"></picture></a>

### 🔥 Web Demos:

- [Main page](https://eyegestures.com/)
- [Game demo](https://eyegestures.com/game)
- [Cinema demo](https://eyegestures.com/cinema)

### 💻 Install
```
pybuild.sh ; python3 -m pip install dist/eyegestures-1.2.2-py3-none-any.whl
```

Note: you may need to change version of package `eyegestures-X.X.X`.

### ⚙️ Run 
```
python3 examples/simple_example.py
```

### 🔧 Develop [WiP - needs update removing all magic numbers]

Minimalistic example:
```python
import VideoCapture #change it to opencv for real applications
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures

gestures = EyeGestures(500,500,250,250,285,115)
cap = VideoCapture(0)  

# Main game loop
running = True
while running:

    # Generate new random position for the cursor
    ret, frame = cap.read()     

    try:
        event = gestures.estimate(
            frame,
            "main",
            True, # set calibration - switch to False to stop calibration
            screen_width,
            screen_height,
            0, 0, 0.8,10)
    
        cursor_x, cursor_y = event.point_screen[0],event.point_screen[1]
    
    except Exception as e:
        print(f"exception: {e}")


```

In example above we can distinguish few parts, like initialization of EyeGestures `full of magic number`. Those numbers shortly describe tracking window size and we will going to document them better in more robust documentation. For now **two first** `500` are size of processing window (it is virtual window used for processing tracked points and cluster them), next two `250` are describing initial x and y positions of tracking window on camera screen, and rest of numbers describe width and height of tracking window on camera screen. 

```python
EyeGestures(500,500,250,250,285,115)
```  

Next part is obtaining estimations from camera frames (if you cannot get estimations, you may try to change color coding or rotation of image - check `simple_example.py`).

```python
event = gestures.estimate(
    frame,
    "main",
    True, # set calibration - switch to False to stop calibration
    screen_width,
    screen_height,
    0, 0, 0.8,10)
```

[NEED UPDATE]
Here `frame` is simple camera frame, but `"main"` is name of camera feed - if you have more than one camera feed you can just change that name for each feed to get accurate tracking (tracker needs past information from the feed, so it allows for context switching).

You can set `True` or `False` for calibration. The best technique for calibration is to switch it to true when user reach one of edge of the screen, and calibrate it for 4 edges. 

The `screen_width` and `screen_hieght` are describing current monitor display size/resolution in pixels, and next two numbers display its `offset` if user has more than two screens. 

The two lasts numbers are `fixation_threshold` which describes thershold after which cursor should be frozen, and last number is `fixation_range` which tells cursor how much noise it can accept in radius to reach and keep fixation. 

### 🌐 Web Embedd [Paid API]

For now more info can be found here: https://eyegestures.com/user_portal

```html
// ... rest of html client ...

<script>
// ... your code ...

function onTile(id, fix, blink) {
  // ... do something here ...
}

function onCalibration() {
  // ... do something here ...
}
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
<script src="https://eyegestures.com/eyeTiles.min.js"></script>
<script>
  EyeTilesAPI(
    key = "YOUR_API_KEY",
    tiles = [1, 2, 1],
    fixThresh = 0.1,
    fixRadius = 500,
    sightGrid = true,
    onTile = onTile,
    onCalibration = onCalibration,
  );
</script>    
```

### 💵 Support the project 

<a href="https://polar.sh/NativeSensors/subscriptions"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/tiers.svg?org=NativeSensors&darkmode"><img alt="Subscription Tiers on Polar" src="https://polar.sh/embed/tiers.svg?org=NativeSensors"></picture></a>
