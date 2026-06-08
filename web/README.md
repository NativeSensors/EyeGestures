## EYEGESTURES
<p align="center">
  <picture>
    <source srcset="https://github.com/NativeSensors/EyeGestures/assets/40773550/ddfc8b96-5a7e-4487-9307-6fbd62e8915e" media="(prefers-color-scheme: light)"/>   
    <source srcset="https://github.com/NativeSensors/EyeGestures/assets/40773550/6d42b8a2-24ea-4cbc-bdb0-ad688ee26c36" media="(prefers-color-scheme: dark)"/>    
   <img width="300px" height="300px"/>
  </picture>
</p>

<a href="https://github.com/pedromxavier/flag-badges">
    <img src="https://raw.githubusercontent.com/pedromxavier/flag-badges/main/badges/PL.svg" alt="made in PL">
</a>

EyeGestures is open source eyetracking software/library using native webcams and phone camers for achieving its goal. The aim of library is to bring accessibility of eye-tracking and eye-driven interfaces without requirement of obtaining expensive hardware.

Our [Mission](https://github.com/NativeSensors/EyeGestures/blob/main/MISSION.md)! 

# EyeGesturesLite

EyeGesturesLite is JavaScript implementation of [EyeGestures algoritm](https://github.com/NativeSensors/EyeGestures). If you need python version, check original repository.

### How does it work?

It is a gaze tracker that uses machine learning and built-in cameras (such as a webcam) to provide gaze tracking for the user. It includes a built-in calibration mode that displays 20 red circles for the user to focus on, along with a blue cursor that follows the user’s gaze. During the calibration process, the cursor will gradually start following user's gaze more and more. By the end of the 20 points, the cursor should be able to independently follow the user’s gaze.

### ⚙️ Try:

[EyeGesturesLite](https://eyegestures.com/tryLite)

### 🔧 Build your own:

#### CDN:

0. External dependencies CDNs:

```html
<script src="https://www.lactame.com/lib/ml/6.0.0/ml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.8.0/math.min.js"></script>
```

1. You need two CDN links:
```html
<link rel="stylesheet" href="https://eyegestures.com/eyegestures.css">
<script src="https://eyegestures.com/eyegestures.js"></script>
```

2. Place `video` element (which can be hidden) somewhere in the page together with status and error divs (can stay invisible):
```html
<video id="video" width="640" height="480" autoplay style="display: none;"></video>
<div id="status" style="display : none;">Initializing...</div>
<div id="error" style="display : none;"></div>
```

3. Then javascript interface code:
```html
<script>

function onPoint(point,calibration){
    point[0]; // x
    point[1]; // y
    calibration; // true - for calibrated data, false if calibration is ongoing
};

const gestures = new EyeGestures('video',onPoint);
// gestures.invisible(); // to disable blue tracker
gestures.start();
</script>
```

#### NPM package [WiP]:

1. Install npm package:
```
npm install eyegestures
```

2. Place `video` element in your DOM (which can be hidden) somewhere in the page together with status and error divs (can stay invisible):
```html
<video id="video_element_id" width="640" height="480" autoplay style="display: none;"></video>
<div id="status" style="display : none;">Initializing...</div>
<div id="error" style="display : none;"></div>
```

3. try to import:
```JS
import EyeGestures from 'eyegestures'; 

const gestures = new EyeGestures("video_element_id",(point,calibration)=>{/*point,calibration*/})
// after this call: gestures.start();
console.log(gestures);
```
>[!Warning]
> EyeGestures needs DOM to operate and its constructor expects to receive video element/camera feed id string.
>

### rules of using

You can use it free of charge as long as you keep our logo. If you want to remove logo then contact: contact@eyegestures.com. 

### 📇 Find us:
- [discord](https://discord.gg/FvagCX8T4h)
- [twitter](https://twitter.com/PW4ltz)
- [daily.dev](https://dly.to/JEe1Sz6vLey)
- email: contact@eyegestures.com

### Troubleshooting:


### 💻 Contributors

<a href="https://github.com/OWNER/REPO/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=NativeSensors/EyeGesturesLite" />
</a>

### 💵 Support the project 

We will be extremely grateful for your support: it helps to keep server running + fuels our brains with coffee. 

Support project on Polar (in exchange we provide access to alphas versions!):

<a href="https://polar.sh/NativeSensors"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe&darkmode"><img alt="Subscribe on Polar" src="https://polar.sh/embed/subscribe.svg?org=NativeSensors&label=Subscribe"></picture></a>

<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="
      https://api.star-history.com/svg?repos=NativeSensors/EyeGesturesLite&type=Date&theme=dark
    "
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="
      https://api.star-history.com/svg?repos=NativeSensors/EyeGesturesLite&type=Date
    "
  />
  <img
    alt="Star History Chart"
    src="https://api.star-history.com/svg?repos=NativeSensors/EyeGesturesLite&type=Date"
  />
</picture>
