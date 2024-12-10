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

> [!IMPORTANT]  
> EyeGestures is a fully volunteer-based project and exists thanks to your donations and support.
>
> <a href="https://buy.polar.sh/polar_cl_H2FqQHunwgXtU7i9mP7VJ95OZ10XVO3vm6MpSimoPPg"><img src="https://polar.sh/embed/product.svg?organizationId=95cd73d8-20dc-4457-9b70-618d9a6a4799&productId=dcf62f17-a82d-4c27-b58f-2db5ca7531ba&productPriceId=17a8e9ba-6705-41fd-a45e-120257b9775d&darkmode" alt="Donation" /></a>


### 💜 Sponsors: 

📢📢 **We are looking for business partnerships and sponsors!** 📢📢

```
For enterprise avoiding GPL3 licensing there is commercial license!
```
We offer custom integration and managed services. For businesses requiring invoices message us `contact@eyegestures.com`.

```
Sponsor us and we can add your link, banner or other promo materials!
```
<!-- POLAR type=ads id=203bbe subscription_benefit_id=bb272b6d-f698-44e3-a417-36a6fa203bbe width=240 height=100 -->

<!-- POLAR-END id=eizdelwu -->

<p align="center">
  <img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/2ad25252-e96e-47d4-b25f-c47ba7f0f4f3" width="300" height="150">
  <img src="https://github.com/NativeSensors/EyeGestures/assets/40773550/923e22a1-7fd7-4c06-9804-256aca22be21" width="300" height="150">
  </p>
<p align="center">
  <img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/3b38d73d-bb6f-4f31-b67d-231ac4cd04cb" width="300" height="150">
  <img src="https://github.com/user-attachments/assets/33e7782b-7977-4f88-ad54-c43d44c6dced" width="300" height="150">
</p>

### 🔨 Projects build with EyeGestures: 

- [EyePilot](https://polar.sh/NativeSensors/products/5fce104c-46ec-4203-892b-a26e0e0ead18)
- [EyePather](https://polar.sh/NativeSensors/posts/eyepather-new-tool-in-eyegestures-ecosystem)
- [EyeFocus](https://polar.sh/NativeSensors/products/3756d557-134e-4e7e-ac50-d850126aa325?ref=producthunt) <- 4th best product on PH!
- Add your project! contact@eyegestures.com or PR

Subscribe and get access to our software:
<p align="left">
  <a href="https://polar.sh/NativeSensors"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe&darkmode"><img alt="Subscribe on Polar" src="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe"></picture></a>

### 💻 Install
```
python3 -m pip install eyeGestures
```

>[!WARNING]
>some users report that mediapipe, scikit-learn or opencv is not installing together with eyegestures. To fix it, just install it with pip.

### ⚙️ Try

Tracker works best when your camera or laptop is at arm's length, similar to how you would typically use it. If you are further away, it may be less responsive for now - currently working on solving this issue.

```
python3 examples/simple_example_v2.py
```

```
python3 examples/simple_example.py [legacy tracker, will become obsolete]
```

### 🔧 Build your own:

#### Using EyeGesture Engine V3 - Faster smaller better:

```python
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

# Initialize gesture engine and video capture
gestures = EyeGestures_v3()
cap = VideoCapture(0)
calibrate = True
screen_width = 500
screen_height= 500

# Process each frame
while True:
  ret, frame = cap.read()
  event, cevent = gestures.step(frame,
    calibrate,
    screen_width,
    screen_height,
    context="my_context")

  if event:
    cursor_x, cursor_y = event.point[0], event.point[1]
    fixation = event.fixation
    saccadess = event.saccadess # saccadess movement detector
    # calibration_radius: radius for data collection during calibration
```

<!-- POLAR type=ads id=eizdelwu subscription_benefit_id=bb272b6d-f698-44e3-a417-36a6fa203bbe width=240 height=100 -->
<!-- POLAR-END id=eizdelwu -->

#### Using EyeGesture Engine V2 - Machine Learning Approach:

```python
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2

# Initialize gesture engine and video capture
gestures = EyeGestures_v2()
cap = VideoCapture(0)  
calibrate = True
screen_width = 500
screen_height= 500

# Process each frame
while True:
  ret, frame = cap.read()
  event, cevent = gestures.step(frame,
    calibrate,
    screen_width,
    screen_height,
    context="my_context")

  if event:
    cursor_x, cursor_y = event.point[0], event.point[1]
    fixation = event.fixation
    # calibration_radius: radius for data collection during calibration
```

<!-- POLAR type=ads id=eizdelwu subscription_benefit_id=bb272b6d-f698-44e3-a417-36a6fa203bbe width=240 height=100 -->
<!-- POLAR-END id=eizdelwu -->

#### Customize:

You can customize your calibration points/map to fit your solutions. Simple copy snippet below, and place your calibration poitns on x,y planes from 0.0 to 1.0. It will be then automatically scaled to your display.

```python
gestures = EyeGestures_v2()
gestures.uploadCalibrationMap([[0,0],[0,1],[1,0],[1,1]])
```

V2 is two stage tracker. It runs V1 under the hood but then uses it as feature extractor for V2 machine learning component, and combines both outputs to generate new gaze point. It is possible to control how much V1 affects V2 by:

```python
gestures.setClassicImpact(N) # setting N = 2 is working best for my testing 
```
This makes that sample obtained from V2 is averaged with N times sample from V1 (same sample copied that many times). In outcome having V2 impacting output in `1/N+1` and V1 `N/N+1`.

It is also worth to know that you can enable hidden calibration for V1 (same calibration when using only V1, but now it is invisible to user):
```python
gestures.enableCNCalib()
```
 
#### Using EyeGesture Engine V1 - Model-Based Approach [not recommended]:

```python
from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v1

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

if event:
  cursor_x, cursor_y = event.point[0], event.point[1]
  fixation = event.fixation
  # calibration_radius: radius for data collection during calibration
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
- [discord](https://discord.gg/sqKdKBJ6)
- [twitter](https://twitter.com/PW4ltz)
- [daily.dev](https://dly.to/JEe1Sz6vLey)
- email: contact@eyegestures.com


### Troubleshooting:

1) some users report that `mediapipe`, `scikit-learn` or `opencv` is not installing together with `eyegestures`. To fix it, just install it with `pip`.

### 💻 Contributors

<a href="https://github.com/OWNER/REPO/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=NativeSensors/EyeGestures" />
</a>

### 💵 Support the project 

We will be extremely grateful for your support: it helps to keep server running + fuels my brain with coffee. 

Support project on Polar (if you want to help we provide access to alphas versions and premium content!):

<a href="https://polar.sh/NativeSensors"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe&darkmode"><img alt="Subscribe on Polar" src="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe"></picture></a>

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

