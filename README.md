```
WARNING: License is work in progress, use for coorporate and business operation my still change. Non-profit and personal use stays free!
```

## 👁️ EyeGestures

EyeGestures is open source eyetracking software/library using native webcams and phone camers for achieving its goal. The aim of library is to bring accessibility of eyetracking and eyedriven interfaces without requirement of obtaining expensive hardware.

<p align="center">
  <img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/2ad25252-e96e-47d4-b25f-c47ba7f0f4f3" width="300" height="150">
<img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/f3132843-063a-439a-8e1c-2385ddfdccda" width="300
" height="150">
</p>
<p align="center">
<img src="https://github.com/NativeSensors/EyeGestures/assets/40773550/84aa7436-6153-49bc-b8e6-ccda535f25e6)" width="600
" height="300">
</p>


### ⭐ Mission 

There is no one size-fits all solution, and we believe that differentiating interfaces brings accessibility to digital spaces. Designing eye-driven interfaces gives more control over computers to those who cannot fully enjoy their capabilities due to different disabilities, as well as an additional way to control computer to rests. 

Such technology should not be paywalled by expensive eye-tracking hardware, especially in case when it is needed to exist in the digital world and operate your computer. Most of the current consumer electronics devices have built-in native cameras, and the current state of research indicates that it is achievable to have eye tracking at reasonable accuracy based on those native cameras. 

Our mission is to bring eye-tracking technology to as many people as possible. 

Our technology is not perfect, but we strive to be.

### 📇 Find us:
- [RSS](https://polar.sh/NativeSensors/rss?auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXRfaWQiOiJkMDYxMDFiOC0xYzYyLTQ1MTYtYjg3YS03NTFhOTM3OTIxZmUiLCJzY29wZXMiOiJhcnRpY2xlczpyZWFkIiwidHlwZSI6ImF1dGgiLCJleHAiOjE3NDMxNjg3ODh9.djoi5ARWHr-xFW_XJ6Fwal3JUT1fAbvx4Npl-daBC5U)
- [discord](https://discord.gg/FV3RYTuV)
- [polar.sh](https://polar.sh/NativeSensors)
- [twitter](https://twitter.com/PW4ltz)
- email: contact@eyegestures.com

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

### 🔧 Develop 

To begin, you instantiate an EyeGestures object with initial Region of Interest (RoI) parameters. These parameters define a preliminary focus area for the tracker within a virtual 500x500 screen space, which helps in locating the user's gaze more efficiently.

Main `EyeGesture` object provides general configuration initial conditions: 

```python
EyeGestures(  
  roi_x = 285
  roi_y = 115
  roi_width = 80
  roi_height = 15
)
```  

The tracker operates within a virtual screen measuring 500x500, where it maps the positions of the pupils and other critical facial features to deduce the user's gaze direction. Within this space, the Region of Interest (RoI) serves as a representation of the user's display, inferred through a combination of eye movement and edge detection during calibration.

After locating the RoI within the 500x500 space, its dimensions are adjusted to fit the resolution used in the estimate function, typically described as `display_width` by `display_height`.

Calibration aims to precisely determine the RoI's dimensions. Prior to calibration, the tracker relies on initial optional parameters, including:

- `roi_x`: The initial x-coordinate of the RoI (ranging from 0 to 500).
- `roi_y`: The initial y-coordinate of the RoI (ranging from 0 to 500).
- `roi_width`: The initial width of the RoI before calibration (ranging from 0 to 500 - x).
- `roi_height`: The initial height of the RoI before calibration (ranging from 0 to 500 - x).

Next part is obtaining estimations from camera frames (if you cannot get estimations, you may try to change color coding or rotation of image - check `simple_example.py`).

```python
event = gestures.estimate(
    image = frame,
    context = "main",
    calibration = True, # set calibration - switch to False to stop calibration
    display_width = screen_width,
    display_height = screen_height,
    display_offset_x = 0, 
    display_offset_y = 0, 
    fixation_freeze = 0.8,
    freeze_radius = 10)
```

- `image` - is cv2 image frame
- `context` - is name given to contect. If name changes then different tracker context is used. Tracker rembers previous points to estimate new one, but those points are assinged to single context. By changing names or passing new ones you can switch and create contextes.
- `calibration` - if `True` then every few seconds tracker is recalibrating, if `False` then tracker setting is frozen. The best approach is to enable calibration when one of the edges is reached. 
- `display_width` - width of display/screen used.
- `display_height` - height of display/screen used.
- `display_offset_x` - offset of x for display/screen used. Use it when having two displays and app is covering all screens, but you want to limit your cursor tracker to only specific display.
- `display_offset_y` - offset of y for display/screen used. Use it when having two displays and app is covering all screens, but you want to limit your cursor tracker to only specific display.
- `fixation_freeze` - threshold of user fixation on one point (it goes from 0.0 to 1.0). If threshold is crossed point is frozen till user breaks `freeze_radius` in pixels.
- `freeze_radius` - distance cursor can move to reach fixation and freezing, if cursor movements are greater than distance then fixation measurement goes down to `0.0`.

```
Gevent event
```

`Gevent` is returned element having all data necessary to use tracker:
 
- `point_screen` is point coordinates on screen
- `blink` is boolean value describing blink event. If `0` no blink occured, if `1` blink occured.
- `fixation` value from `0.0` to `1.0` describing level of user fixation.

Entire program: 

```python
import VideoCapture #change it to opencv for real applications
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures

gestures = EyeGestures(
  roi_x = 285
  roi_y = 115
  roi_width = 80
  roi_height = 15
)

cap = VideoCapture(0)  

# Main game loop
running = True
while running:

    # Generate new random position for the cursor
    ret, frame = cap.read()     

    event = gestures.estimate(
        frame,
        "main",
        True, # set calibration - switch to False to stop calibration
        screen_width,
        screen_height,
        0, 0, 0.8,10)

    cursor_x, cursor_y = event.point_screen[0],event.point_screen[1]

```


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

### rules of using

If you are building publicly available product, and have no commercial license, please mention us somewhere in your interface. 

**Promo Materials:**

https://github.com/NativeSensors/EyeGestures/assets/40773550/4ca842b9-ba32-4ffd-b2e4-179ff67ee47f

![PoweredByEyeGestures_small](https://github.com/NativeSensors/EyeGestures/assets/40773550/4ca842b9-ba32-4ffd-b2e4-179ff67ee47f)

https://github.com/NativeSensors/EyeGestures/assets/40773550/6a7c74b5-b069-4eec-bc96-3a6bb4159b37

![PoweredByEyeGestures_tiny](https://github.com/NativeSensors/EyeGestures/assets/40773550/6a7c74b5-b069-4eec-bc96-3a6bb4159b37)


### 💻 Contributors

<a href="https://github.com/OWNER/REPO/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=NativeSensors/EyeGestures" />
</a>

### 💵 Support the project 

<a href="https://polar.sh/NativeSensors/subscriptions"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/tiers.svg?org=NativeSensors&darkmode"><img alt="Subscription Tiers on Polar" src="https://polar.sh/embed/tiers.svg?org=NativeSensors"></picture></a>
