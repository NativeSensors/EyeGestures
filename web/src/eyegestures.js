const __eyeGesturesScriptUrl = (document.currentScript && document.currentScript.src) || window.location.href;
let __eyeGesturesEngineModulePromise = null;

function __resolveEngineModuleUrl() {
    if (window.EyeGesturesEngineModuleUrl) {
        return window.EyeGesturesEngineModuleUrl;
    }
    console.log("__eyeGesturesScriptUrl: ", __eyeGesturesScriptUrl);
    return new URL('EyegesturesEngine.js', __eyeGesturesScriptUrl).href;
}

function __loadEngineModule() {
    if (!__eyeGesturesEngineModulePromise) {
        __eyeGesturesEngineModulePromise = import(__resolveEngineModuleUrl());
    }
    return __eyeGesturesEngineModulePromise;
}

VERSION = "4.0.0";
class EyeGestures{ // strip export default before making cdn/web embeddable version 
    constructor(videoElement_ID, onGaze, dynamic_recalib = true, sampling_fps = 30, show_settings = true)
    {
        const cursor = document.createElement('div');
        cursor.id = "cursor";
        cursor.style.display = "None";
        document.body.appendChild(cursor);
        const calib_cursor = document.createElement('div');
        calib_cursor.id = "calib_cursor";
        calib_cursor.style.display = "None";

        this.engine = null;
        this.onGaze = onGaze;
        this.run = false;
        this.__invisible = false;
        this.screen_width = 0;
        this.screen_height = 0;
        this.dynamic_recalib = dynamic_recalib;
        // Calibration data acquisition rate; gaze tracking itself keeps running at full frame rate.
        this.sampling_fps = sampling_fps;
        // Show the settings (FPS cap + dynamic calibration) section inside the banner
        this.show_settings = show_settings;
        this.__settings_open = false;

        this.__createBanner();

        document.body.appendChild(calib_cursor);

        this.updateViewportSize();

        if (window.isSecureContext) {
            this.init(videoElement_ID);
        }
        else {
            console.error('This application requires a secure context (HTTPS or localhost)');
        }
        
    }

    updateViewportSize() {
        this.screen_width = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        this.screen_height = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
    }

    // Banner (logo + eye canvas) with an expandable settings section
    __createBanner() {
        const logoDiv = document.createElement('div');
        logoDiv.id = "logoDivEyeGestures";
        logoDiv.style.width = this.show_settings ? "240px" : "200px";
        logoDiv.style.height = "60px";
        logoDiv.style.position = "fixed";
        logoDiv.style.bottom = "10px";
        logoDiv.style.right = "10px";
        logoDiv.style.zIndex = "9999";
        logoDiv.style.background = "black";
        logoDiv.style.borderRadius = "10px";
        logoDiv.style.display = "none";
        logoDiv.style.flexDirection = "column";
        logoDiv.style.alignItems = "stretch";
        logoDiv.style.overflow = "hidden";
        logoDiv.style.color = "#fff";
        logoDiv.style.fontFamily = "Arial, sans-serif";
        logoDiv.style.fontSize = "12px";
        logoDiv.onclick = function() {
            window.location.href = "https://eyegestures.com/";
        };

        const bar = document.createElement('div');
        bar.id = "barDivEyeGestures";
        bar.style.display = "flex";
        bar.style.flexDirection = "row";
        bar.style.alignItems = "center";
        bar.style.justifyContent = "space-between";

        const logo = document.createElement('div');
        logo.style.margin = "10px";
        logo.innerHTML = '<img src="https://eyegestures.com/logoEyeGesturesNew.png" alt="Logo" width="120px">';
        bar.appendChild(logo);

        const canvas = document.createElement('canvas');
        canvas.id = "output_canvas";
        canvas.width = "50"; 
        canvas.height = "50";
        canvas.style.margin = "5px";
        canvas.style.borderRadius = "10px";
        canvas.style.border = "none";
        canvas.style.background = "#222";
        bar.appendChild(canvas);

        if (this.show_settings) {
            const gear = document.createElement('button');
            gear.id = "settingsButtonEyeGestures";
            gear.type = "button";
            gear.textContent = "⚙";
            gear.title = "EyeGestures settings";
            gear.style.width = "30px";
            gear.style.height = "30px";
            gear.style.margin = "5px";
            gear.style.flex = "0 0 auto";
            gear.style.padding = "0";
            gear.style.border = "none";
            gear.style.borderRadius = "6px";
            gear.style.background = "#222";
            gear.style.color = "#fff";
            gear.style.fontSize = "16px";
            gear.style.cursor = "pointer";
            gear.onclick = (event) => {
                event.stopPropagation();
                this.toggleBannerSettings();
            };
            bar.appendChild(gear);
        }

        logoDiv.appendChild(bar);

        if (this.show_settings) {
            logoDiv.appendChild(this.__createSettingsPanel());
        }

        document.body.appendChild(logoDiv);

        this.__syncBannerSettings();
    }

    __createSettingsPanel() {
        const panel = document.createElement('div');
        panel.id = "settingsPanelEyeGestures";
        panel.style.display = "none";
        panel.style.flexDirection = "column";
        panel.style.padding = "0 10px 10px 10px";
        // clicks inside the panel must not follow the banner link
        panel.onclick = (event) => event.stopPropagation();

        const fpsRow = document.createElement('div');
        fpsRow.style.display = "flex";
        fpsRow.style.flexDirection = "row";
        fpsRow.style.alignItems = "center";
        fpsRow.style.justifyContent = "space-between";

        const fpsLabel = document.createElement('span');
        fpsLabel.textContent = "FPS cap";
        fpsRow.appendChild(fpsLabel);

        const fpsValue = document.createElement('span');
        fpsValue.id = "fpsValueEyeGestures";
        fpsValue.style.fontWeight = "bold";
        fpsRow.appendChild(fpsValue);

        const slider = document.createElement('input');
        slider.id = "fpsSliderEyeGestures";
        slider.type = "range";
        slider.min = "0";
        slider.max = "60";
        slider.step = "1";
        slider.value = String(this.sampling_fps);
        slider.style.width = "100%";
        slider.style.margin = "5px 0";
        slider.style.accentColor = "#5e17eb";
        slider.style.cursor = "pointer";
        slider.onclick = (event) => event.stopPropagation();
        slider.oninput = (event) => {
            event.stopPropagation();
            this.setSamplingFps(Number(event.target.value));
        };

        const calibRow = document.createElement('div');
        calibRow.style.display = "flex";
        calibRow.style.flexDirection = "row";
        calibRow.style.alignItems = "center";
        calibRow.style.justifyContent = "space-between";

        const calibLabel = document.createElement('span');
        calibLabel.textContent = "Dynamic calib";
        calibRow.appendChild(calibLabel);

        const toggle = document.createElement('button');
        toggle.id = "dynamicCalibToggleEyeGestures";
        toggle.type = "button";
        toggle.style.padding = "4px 12px";
        toggle.style.border = "none";
        toggle.style.borderRadius = "5px";
        toggle.style.color = "#fff";
        toggle.style.fontSize = "12px";
        toggle.style.cursor = "pointer";
        toggle.onclick = (event) => {
            event.stopPropagation();
            this.setDynamicRecalib(!this.dynamic_recalib);
        };
        calibRow.appendChild(toggle);

        panel.appendChild(fpsRow);
        panel.appendChild(slider);
        panel.appendChild(calibRow);

        return panel;
    }

    // Expand/collapse the settings section of the banner
    setBannerSettings(open) {
        const logoDiv = document.getElementById("logoDivEyeGestures");
        const panel = document.getElementById("settingsPanelEyeGestures");
        if (!logoDiv || !panel) {
            return;
        }
        this.__settings_open = open;
        panel.style.display = open ? "flex" : "none";
        logoDiv.style.width = open ? "260px" : "240px";
        logoDiv.style.height = open ? "auto" : "60px";
    }

    toggleBannerSettings() {
        this.setBannerSettings(!this.__settings_open);
    }

    __syncBannerSettings() {
        const slider = document.getElementById("fpsSliderEyeGestures");
        const fpsValue = document.getElementById("fpsValueEyeGestures");
        const toggle = document.getElementById("dynamicCalibToggleEyeGestures");
        if (slider) {
            slider.value = String(this.sampling_fps);
        }
        if (fpsValue) {
            fpsValue.textContent = this.sampling_fps > 0 ? `${this.sampling_fps} fps` : "off";
        }
        if (toggle) {
            toggle.textContent = this.dynamic_recalib ? "ON" : "OFF";
            toggle.style.background = this.dynamic_recalib ? "#5e17eb" : "#555";
        }
    }

    showUpCalibrationInstructions(onRead) {
        // Create content container
        // const content = document.createElement('div');
        // content.style.textAlign = 'center';
        // content.style.color = '#fff';
        // content.style.fontFamily = 'Arial, sans-serif';

        // // Create instructional text
        // const instructionText1 = document.createElement('h3');
        // instructionText1.textContent = 'EyeGestures Upcalibration:';
        // instructionText1.style.fontSize = '1.5rem';
        // instructionText1.style.marginBottom = '20px';

        // const instructionText2 = document.createElement('p');
        // instructionText2.innerHTML = 'We need to improve calibration. Focus on <span style="color: #ff5757; font-weight: bold;">25 red circles</span>.';
        // instructionText2.style.marginBottom = '20px';
        
        // const instructionText3 = document.createElement('p');
        // instructionText3.innerHTML = 'The <span style="color: #5e17eb; font-weight: bold;">blue circle</span> is your estimated gaze. With every calibration point, the tracker will gradually listen more and more to your gaze.';
        // instructionText3.style.marginBottom = '20px';

        // // Append elements to content
        // content.appendChild(instructionText1);
        // content.appendChild(instructionText2);
        // content.appendChild(instructionText3);
        // content.appendChild(button);
    }

    showCalibrationInstructions(onRead) {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.id = 'calibrationOverlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '1000';

        // Create content container
        const content = document.createElement('div');
        content.style.textAlign = 'center';
        content.style.color = '#fff';
        content.style.fontFamily = 'Arial, sans-serif';

        // Create instructional text
        const instructionText1 = document.createElement('h3');
        instructionText1.textContent = 'EyeGestures Calibration:';
        instructionText1.style.fontSize = '1.5rem';
        instructionText1.style.marginBottom = '20px';

        const instructionText2 = document.createElement('p');
        instructionText2.innerHTML = 'To calibrate properly you need to gaze on <span style="color: #ff5757; font-weight: bold;">25 red circles</span>.';
        instructionText2.style.marginBottom = '20px';
        
        const instructionText3 = document.createElement('p');
        instructionText3.innerHTML = 'The <span style="color: #5e17eb; font-weight: bold;">blue circle</span> is your estimated gaze. With every calibration point, the tracker will gradually listen more and more to your gaze.';
        instructionText3.style.marginBottom = '20px';

        // Create button
        const button = document.createElement('button');
        button.textContent = 'Continue';
        button.style.padding = '10px 20px';
        button.style.fontSize = '1rem';
        button.style.border = 'none';
        button.style.borderRadius = '5px';
        button.style.backgroundColor = '#5e17eb';
        button.style.color = '#fff';
        button.style.cursor = 'pointer';

        // Button click event to remove overlay
        button.addEventListener('click', () => {
            document.body.removeChild(overlay);
            onRead();
        });
        // Append elements to content
        content.appendChild(instructionText1);
        content.appendChild(instructionText2);
        content.appendChild(instructionText3);
        content.appendChild(button);

        // Append content to overlay
        overlay.appendChild(content);

        // Append overlay to body
        document.body.appendChild(overlay);

        setTimeout(() => {
            document.body.removeChild(overlay);
            onRead();
        },15000)
    }


    // Status update function
    updateStatus(message) {
        document.getElementById('status').textContent = message;
    }

    // Error display function
    showError(message) {
        const errorElement = document.getElementById('error');
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    // Function to load script with promise
    loadScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // Main initialization
    async init(videoElement_id) {
        try {
            this.updateViewportSize();
            this.updateStatus('Loading EyeGestures engine...');
            const engineModule = await __loadEngineModule();
            await engineModule.default();
            this.engine = new engineModule.EyeGesturesEngineWasm(this.screen_width, this.screen_height, this.dynamic_recalib);
            this.engine.set_sampling_fps(this.sampling_fps);

            this.updateStatus('Loading MediaPipe library...');
            
            // Load MediaPipe library
            await this.loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@0.3/drawing_utils.js');
            await this.loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh@0.4.1633559619/face_mesh.js');
            
            this.updateStatus('MediaPipe library loaded, initializing...');
            
            if (typeof FaceMesh === 'undefined') {
                throw new Error('FaceMesh is not defined. Library not loaded correctly.');
            }

            await this.setupMediaPipe(videoElement_id);
        } catch (error) {
            console.error('Initialization error:', error);
            this.showError('Initialization error: ' + error.message);
        }
    }

    async setupMediaPipe(videoElement_id) {
        try {
            // Initialize FaceMesh solution
            const faceMesh = new FaceMesh({
                locateFile: (file) => {
                    console.log("Loading file:", file);
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh@0.4.1633559619/${file}`;
                }
            });

            // Set options for FaceMesh
            faceMesh.setOptions({
                maxNumFaces: 1,
                refineLandmarks: true,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            // Initialize the FaceMesh instance
            await faceMesh.initialize();
            this.updateStatus('FaceMesh initialized successfully');

            // Set callback for the results
            faceMesh.onResults(this.onFaceMeshResults.bind(this));

            // Access video stream
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: {} 
            });
            
            const videoElement = document.getElementById(videoElement_id);
            videoElement.srcObject = stream;

            // Wait for video to be loaded
            videoElement.onloadeddata = () => {
                this.updateStatus('Video stream started');
                videoElement.play();
                requestAnimationFrame(processFrame);
            };

            async function processFrame() {
                const videoElement = document.getElementById("video");
                if (videoElement.readyState !== videoElement.HAVE_ENOUGH_DATA) {
                    requestAnimationFrame(processFrame);
                    return;
                }

                const canvas = document.getElementById("output_canvas");
                const ctx = canvas.getContext("2d");
                try {
                    // ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
                    ctx.save();
                    ctx.scale(-1, 1); // Flip horizontally (invert x-axis)
                    ctx.translate(-canvas.width, 0); // Adjust translation to ensure the image is drawn correctly
                    faceMesh.send({ image: videoElement });
                    ctx.restore();
                } catch (error) {
                    console.error('Error processing frame:', error);
                    showError('Error processing frame: ' + error.message);
                }
                requestAnimationFrame(processFrame);
            }

        } catch (error) {
            console.error('Error initializing MediaPipe:', error);
            showError('Error initializing MediaPipe: ' + error.message);
        }
    }

    onFaceMeshResults(results) {
        if ((!results.multiFaceLandmarks || !results.multiFaceLandmarks.length) || !this.run) {
            return;
        }

        if (!this.engine) {
            return;
        }

        this.updateViewportSize();

        // Define eye keypoints before using them
        const LEFT_EYE_KEYPOINTS = [
            33, 133, 160, 159, 158, 157, 173, 155, 154, 153, 144, 145, 153, 246, 468
        ];
        const RIGHT_EYE_KEYPOINTS = [
            362, 263, 387, 386, 385, 384, 398, 382, 381, 380, 374, 373, 374, 466, 473
        ];

        let landmarks = results.multiFaceLandmarks[0];
        const flattened = new Float64Array(landmarks.flatMap(point => [point.x, point.y]));
        const output = this.engine.process(flattened);
        const x = output[0];
        const y = output[1];
        const calibrating = output[2] === 1;
        const x_calib = output[3];
        const y_calib = output[4];

        // visual layer
        let l_landmarks = LEFT_EYE_KEYPOINTS.map(index => landmarks[index]);
        let r_landmarks = RIGHT_EYE_KEYPOINTS.map(index => landmarks[index]);
        let scale_x = 1;
        let scale_y = 1;
        let offset_x = 0;
        let offset_y = 0;
        let width = x - offset_x;
        let height = y - offset_y;
        const canvas = document.getElementById("output_canvas");
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let left_eye_coordinates = [];
        let right_eye_coordinates = [];

        ctx.fillStyle = '#ff5757';
        l_landmarks.forEach(landmark => {
            left_eye_coordinates.push(
                [
                    (((landmark.x- offset_x)/width) * scale_x ),
                    (((landmark.y- offset_y)/height) * scale_y )
                ]
            );
            ctx.beginPath();
            ctx.arc(
                landmark.x * canvas.width,
                landmark.y * canvas.height,
                3, // radius
                0,
                2 * Math.PI
            );
            ctx.fill();
        });

        // Draw dots for each landmark
        ctx.fillStyle = '#5e17eb';
        r_landmarks.forEach(landmark => {
            right_eye_coordinates.push(
                [
                    (((landmark.x- offset_x)/width) * scale_x ),
                    (((landmark.y- offset_y)/height) * scale_y )
                ]
            );
            ctx.beginPath();
            ctx.arc(
                landmark.x * canvas.width,
                landmark.y * canvas.height,
                3, // radius
                0,
                2 * Math.PI
            );
            ctx.fill();
        });

        let cursor = document.getElementById("cursor");
        let left = Math.min(Math.max(x,0),this.screen_width)
        let top = Math.min(Math.max(y,0),this.screen_height)
        cursor.style.left = `${left - 25}px`;
        cursor.style.top = `${top - 25}px`;
        let calib_cursor = document.getElementById("calib_cursor");
        let calib_left = Math.min(Math.max(x_calib,0),this.screen_width);
        let calib_top = Math.min(Math.max(y_calib,0),this.screen_height);
        calib_cursor.style.left = `${calib_left - 100}px`;
        calib_cursor.style.top = `${calib_top - 100}px`;

        if(!calibrating){
            calib_cursor.style.display = "none";
        }else{
            calib_cursor.style.display = "block";
        }

        this.onGaze([x, y], calibrating);
    }

    __run(){
        this.run = true;
    }

    start(){
        const logoDivEyeGestures = document.getElementById("logoDivEyeGestures");
        logoDivEyeGestures.style.display = "flex";

        this.showCalibrationInstructions(this.__run.bind(this));

        if(!this.__invisible){
            let cursor = document.getElementById("cursor");
            cursor.style.display = "block";
        }

        let calib_cursor = document.getElementById("calib_cursor");
        calib_cursor.style.display = "block";
        // this.run = true;
    };

    invisible()
    {
        this.__invisible = true;
        let cursor = document.getElementById("cursor");
        cursor.style.display = "none";
    }

    visible()
    {
        this.__invisible = false;
        let cursor = document.getElementById("cursor");
        cursor.style.display = "block";
    }

    stop(){
        this.run = false;
        console.log("stop");
    };

    recalibrate(){
        if (this.engine) {
            this.engine.recalibrate();
        }
    };

    setSamplingFps(fps){
        this.sampling_fps = fps;
        if (this.engine) {
            this.engine.set_sampling_fps(fps);
        }
        this.__syncBannerSettings();
    };

    setDynamicRecalib(enabled){
        this.dynamic_recalib = enabled;
        if (this.engine) {
            this.engine.set_dynamic_recalib(enabled);
        }
        this.__syncBannerSettings();
    };

    addPointToCalibration(x, y){
        if (this.engine) {
            this.engine.add_calibration_point(x, y);
        }
    };
}
