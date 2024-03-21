## 👁️ EyeGestures

EyeGestures is open source eyetracking software/library using native webcams and phone camers for achieving its goal. The aim of library is to bring accessibility of eyetracking and eyedriven interfaces without requirement of obtaining expensive hardware.

<p align="center">
  <img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/2ad25252-e96e-47d4-b25f-c47ba7f0f4f3" width="300" height="150">
<img src="https://github.com/PeterWaIIace/PeterWaIIace/assets/40773550/f3132843-063a-439a-8e1c-2385ddfdccda" width="300
" height="150">
</p>

### ⭐ Mission 

There is no one size fits all solution, and we believe that differentiating interfaces brings accessibility to digital spaces. Desiging eye-driven interfaces gives more control over computers to those who cannot fully enjoy their capabilities due to different disabilities, as well as gives additional way to control your computer for rests. 

Such technology should not be paywalled by expensive eyetrackign hardware, especially in case when it is needed to exist in digital world and operate your computer. Most of current consumer electronics devices have built-in natively cameras and current state of research shows that it is achievable to have eyetracking at reasonable accurace based on those native cameras. 

With such establish situation, we aim to bring such technology to as many people as it is possible. 

Our technology is not perfect, but strive to be.    

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

Minimalistic example:
```
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

```
EyeGestures(500,500,250,250,285,115)
```  

Next part is obtaining estimations from camera frames (if you cannot get estimations, you may try to change color coding or rotation of image - check `simple_example.py`).

```
event = gestures.estimate(
    frame,
    "main",
    True, # set calibration - switch to False to stop calibration
    screen_width,
    screen_height,
    0, 0, 0.8,10)
```

Here `frame` is simple camera frame, but `"main"` is name of camera feed - if you have more than one camera feed you can just change that name for each feed to get accurate tracking (tracker needs past information from the feed, so it allows for context switching).

You can set `True` or `False` for calibration. The best technique for calibration is to switch it to true when user reach one of edge of the screen, and calibrate it for 4 edges. 

The `screen_width` and `screen_hieght` are describing current monitor display size/resolution in pixels, and next two numbers display its `offset` if user has more than two screens. 

The two lasts numbers are `fixation_threshold` which describes thershold after which cursor should be frozen, and last number is `fixation_range` which tells cursor how much noise it can accept in radius to reach and keep fixation. 


### 💵 Support the project 

<a href="https://polar.sh/PeterWaIIace/subscriptions"><picture><source media="(prefers-color-scheme: dark)" srcset="https://polar.sh/embed/tiers.svg?org=PeterWaIIace&darkmode"><img alt="Subscription Tiers on Polar" src="https://polar.sh/embed/tiers.svg?org=PeterWaIIace"></picture></a>
