<p align="center">
  <picture>
    <source srcset="https://github.com/NativeSensors/EyeGestures/assets/40773550/ddfc8b96-5a7e-4487-9307-6fbd62e8915e" media="(prefers-color-scheme: light)"/>   
    <source srcset="https://github.com/NativeSensors/EyeGestures/assets/40773550/6d42b8a2-24ea-4cbc-bdb0-ad688ee26c36" media="(prefers-color-scheme: dark)"/>    
   <img width="300px" height="300px"/>
  </picture>
</p>

## EYEGESTURES


EyeGestures is open source eyetracking software/library using native webcams and phone camers for achieving its goal. The aim of library is to bring accessibility of eye-tracking and eye-driven interfaces without requirement of obtaining expensive hardware.

Our [Mission](https://github.com/NativeSensors/EyeGestures/blob/main/MISSION.md)! 

![PyPI - Downloads](https://img.shields.io/pypi/dm/eyeGestures)
<a href="https://polar.sh/NativeSensors"><img src="https://polar.sh/embed/seeks-funding-shield.svg?org=NativeSensors" /></a>
### 💜 Sponsors: 

```
For enterprise avoiding GPL3 licensing there is commercial license!
```
We offer custom integration and managed services. For businesses requiring invoices message us `contact@eyegestures.com`.

```
Sponsor us and we can add your link, banner or other promo materials!
```
<!-- POLAR type=ads id=eizdelwu subscription_benefit_id=bb272b6d-f698-44e3-a417-36a6fa203bbe width=240 height=100 -->



<!-- POLAR-END id=eizdelwu -->

<p align="center">
  <img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/2ad25252-e96e-47d4-b25f-c47ba7f0f4f3" width="300" height="150">
<img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/f3132843-063a-439a-8e1c-2385ddfdccda" width="300
" height="150">
</p>
<p align="center">
  <img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/3b38d73d-bb6f-4f31-b67d-231ac4cd04cb" width="300" height="150">
  <img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/1715b4df-7ac3-479e-b51a-f6d800ea8ea5" width="300" height="150">
</p>

<p align="center">
  <a href="https://polar.sh/NativeSensors"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe&darkmode"><img alt="Subscribe on Polar" src="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe"></picture></a>
</p>
<p align="center">
  <a href="https://ko-fi.com/Y8Y1SGTBV"><picture><img src="https://ko-fi.com/img/githubbutton_sm.svg"/></a>
</p>

### 🔨 Projects build with EyeGestures: 

- [EyePilot](https://polar.sh/NativeSensors/products/5fce104c-46ec-4203-892b-a26e0e0ead18)
- [EyePather](https://polar.sh/NativeSensors/posts/eyepather-new-tool-in-eyegestures-ecosystem)
- Add your project! contact@eyegestures.com or PR

### 💻 Install
```
python3 -m pip install eyeGestures
```

### ⚙️ Run 
```
python3 examples/simple_example.py
```

```
python3 examples/simple_example_v2.py
```

### 🔧 How to use:

#### Using EyeGesture Engine V2 - Machine Learning Approach:

```python
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures_v2

# Initialize gesture engine and video capture
gestures = EyeGestures_v2()
cap = VideoCapture(0)  
ret, frame = cap.read()
calibrate = True
screen_width = 500
screen_height= 500

# Process each frame
event, cevent = gestures.step(frame, True, screen_width, screen_height)

cursor_x, cursor_y = event.point[0], event.point[1]
# calibration_radius: radius for data collection during calibration
```

<!-- POLAR type=ads id=eizdelwu subscription_benefit_id=bb272b6d-f698-44e3-a417-36a6fa203bbe width=240 height=100 -->



<!-- POLAR-END id=eizdelwu -->

#### Using EyeGesture Engine V1 - Model-Based Approach:

```python
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures_v1

# Initialize gesture engine with RoI parameters
gestures = EyeGestures_v1()

cap = VideoCapture(0)  
ret, frame = cap.read()
calibrate = True
screen_width = 500
screen_height= 500

# Obtain estimations from camera frames
event, cevent = gestures.estimate(
    frame,
    "main",
    calibrate,  # set calibration - switch to False to stop calibration
    screen_width,
    screen_height,
    0, 0, 0.8, 10
)
cursor_x, cursor_y = event.point[0], event.point[1]
# cevent - is calibration event
```

Feel free to copy and paste the relevant code snippets for your project.

### 🔥 Web Demos:

- [Main page](https://eyegestures.com/)
- [Game demo](https://eyegestures.com/game)
- [Cinema demo](https://eyegestures.com/cinema)
- [Restaurant](https://eyegestures.com/restaurant)

### rules of using

If you are building publicly available product, and have no commercial license, please mention us somewhere in your interface. 

### 📇 Find us:
- [RSS](https://polar.sh/NativeSensors/rss?auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXRfaWQiOiJkMDYxMDFiOC0xYzYyLTQ1MTYtYjg3YS03NTFhOTM3OTIxZmUiLCJzY29wZXMiOiJhcnRpY2xlczpyZWFkIiwidHlwZSI6ImF1dGgiLCJleHAiOjE3NDMxNjg3ODh9.djoi5ARWHr-xFW_XJ6Fwal3JUT1fAbvx4Npl-daBC5U)
- [discord](https://discord.gg/KmEgWVgn)
- [twitter](https://twitter.com/PW4ltz)
- [daily.dev](https://dly.to/JEe1Sz6vLey)
- email: contact@eyegestures.com

Follow us on polar (it costs nothing but you help project!):

<a href="https://polar.sh/NativeSensors"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe&darkmode"><img alt="Subscribe on Polar" src="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe"></picture></a>

### 📢 Announcements:

<a href="https://polar.sh/NativeSensors/posts"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/posts.svg?org=NativeSensors&darkmode"><img alt="Posts on Polar" src="https://polar.sh/embed/posts.svg?org=NativeSensors"></picture></a>

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

