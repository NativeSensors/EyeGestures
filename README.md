

![PyPI - Downloads](https://img.shields.io/pypi/dm/eyeGestures)

```
For enterprise avoiding GPL3 licensing there is commercial license!
```
We offer custom integration and managed services. For businesses requiring invoices message us `contact@eyegestures.com`.

### 💜 Sponsors: 

```
Sponsor us and we can add your link, banner or other promo materials!
```
<!-- POLAR type=ads id=eizdelwu subscription_benefit_id=bb272b6d-f698-44e3-a417-36a6fa203bbe width=240 height=100 -->



<!-- POLAR-END id=eizdelwu -->

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

There is no one-size-fits-all solution, and we believe that diversifying interfaces brings accessibility to digital spaces. Designing eye-driven interfaces provides greater control over computers for those unable to fully utilize their capabilities due to various disabilities, while also offering an additional means of computer control for all users.

Such technology should not be hindered by expensive eye-tracking hardware, particularly when it is essential for individuals to navigate the digital realm and operate their computers. Many current consumer electronics devices feature built-in native cameras, and ongoing research suggests that achieving eye tracking with reasonable accuracy using these native cameras is feasible.

Our mission is to democratize eye-tracking technology, making it accessible to as many people as possible.

While our technology is not flawless, we are committed to continuous improvement and strive for excellence.

### 📢 Announcements:

<a href="https://polar.sh/NativeSensors/posts"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/posts.svg?org=NativeSensors&darkmode"><img alt="Posts on Polar" src="https://polar.sh/embed/posts.svg?org=NativeSensors"></picture></a>

### 📇 Find us:
- [RSS](https://polar.sh/NativeSensors/rss?auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXRfaWQiOiJkMDYxMDFiOC0xYzYyLTQ1MTYtYjg3YS03NTFhOTM3OTIxZmUiLCJzY29wZXMiOiJhcnRpY2xlczpyZWFkIiwidHlwZSI6ImF1dGgiLCJleHAiOjE3NDMxNjg3ODh9.djoi5ARWHr-xFW_XJ6Fwal3JUT1fAbvx4Npl-daBC5U)
- [discord](https://discord.gg/FV3RYTuV)
- [twitter](https://twitter.com/PW4ltz)
- email: contact@eyegestures.com

Follow us on polar (it costs nothing but you help project!):

<a href="https://polar.sh/NativeSensors"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe&darkmode"><img alt="Subscribe on Polar" src="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe"></picture></a>

### 🔥 Web Demos:

- [Main page](https://eyegestures.com/)
- [Game demo](https://eyegestures.com/game)
- [Cinema demo](https://eyegestures.com/cinema)
- [Restaurant](https://eyegestures.com/restaurant)

### 💻 Install
```
python3 -m pip install eyeGestures
```

Note: you may need to change version of package `eyegestures-X.X.X`.

### ⚙️ Run 
```
python3 examples/simple_example.py
```

### 🪟 Run Windows App 
```
python3 apps/win_app.py
```

Or download it from [`releases`](https://github.com/NativeSensors/EyeGestures/releases/tag/1.3.4_App_0.0.3)

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

<img src="https://github.com/NativeSensors/EyeGestures/assets/40773550/4ca842b9-ba32-4ffd-b2e4-179ff67ee47f" width="300
">

https://github.com/NativeSensors/EyeGestures/assets/40773550/6a7c74b5-b069-4eec-bc96-3a6bb4159b37

<img src="https://github.com/NativeSensors/EyeGestures/assets/40773550/6a7c74b5-b069-4eec-bc96-3a6bb4159b37" width="200
">


### 💻 Contributors

<a href="https://github.com/OWNER/REPO/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=NativeSensors/EyeGestures" />
</a>

### 💵 Support the project 

<a href="https://polar.sh/NativeSensors/subscriptions"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/tiers.svg?org=NativeSensors&darkmode"><img alt="Subscription Tiers on Polar" src="https://polar.sh/embed/tiers.svg?org=NativeSensors"></picture></a>

<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="
      https://api.star-history.com/svg?repos=NativeSensors/EyeGestures&type=Date&theme=dark
    "
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="
      https://api.star-history.com/svg?repos=NativeSensors/EyeGestures&type=Date
    "
  />
  <img
    alt="Star History Chart"
    src="https://api.star-history.com/svg?repos=NativeSensors/EyeGestures&type=Date"
  />
</picture>

