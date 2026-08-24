/**
 * MediaPipe Holistic Studio - Client Application Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const tabWebcam = document.getElementById('tabWebcam');
    const tabUpload = document.getElementById('tabUpload');
    const webcamActions = document.getElementById('webcamActions');
    const uploadActions = document.getElementById('uploadActions');

    const toggleFace = document.getElementById('toggleFace');
    const toggleTesselation = document.getElementById('toggleTesselation');
    const togglePose = document.getElementById('togglePose');
    const toggleHands = document.getElementById('toggleHands');
    const toggleAnalytics = document.getElementById('toggleAnalytics');

    const btnToggleCamera = document.getElementById('btnToggleCamera');
    const btnSnapshot = document.getElementById('btnSnapshot');
    const btnFullscreen = document.getElementById('btnFullscreen');
    const cameraStatusBadge = document.getElementById('cameraStatusBadge');
    const cameraStatusText = document.getElementById('cameraStatusText');
    const fpsValue = document.getElementById('fpsValue');

    const liveStreamImg = document.getElementById('liveStreamImg');
    const uploadedImageResult = document.getElementById('uploadedImageResult');
    const uploadedVideoResult = document.getElementById('uploadedVideoResult');
    const viewportPlaceholder = document.getElementById('viewportPlaceholder');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const spinnerText = document.getElementById('spinnerText');

    const dropzone = document.getElementById('mediaDropzone');
    const fileInput = document.getElementById('fileInput');
    const btnBrowseFile = document.getElementById('btnBrowseFile');

    // Telemetry display elements
    const valPosture = document.getElementById('valPosture');
    const valGesture = document.getElementById('valGesture');
    const valTorsoTilt = document.getElementById('valTorsoTilt');
    const valShoulderTilt = document.getElementById('valShoulderTilt');

    const barLeftElbow = document.getElementById('barLeftElbow');
    const degLeftElbow = document.getElementById('degLeftElbow');
    const barRightElbow = document.getElementById('barRightElbow');
    const degRightElbow = document.getElementById('degRightElbow');

    const barLeftKnee = document.getElementById('barLeftKnee');
    const degLeftKnee = document.getElementById('degLeftKnee');
    const barRightKnee = document.getElementById('barRightKnee');
    const degRightKnee = document.getElementById('degRightKnee');

    const cntFace = document.getElementById('cntFace');
    const cntPose = document.getElementById('cntPose');
    const cntLeftHand = document.getElementById('cntLeftHand');
    const cntRightHand = document.getElementById('cntRightHand');

    const btnToggleJson = document.getElementById('btnToggleJson');
    const jsonViewer = document.getElementById('jsonViewer');
    const jsonChevron = document.getElementById('jsonChevron');

    // State Variables
    let isCameraActive = false;
    let telemetryInterval = null;
    let currentMode = 'webcam';

    // Helper: Build Stream URL with query parameters
    function getStreamUrl() {
        const params = new URLSearchParams({
            face: toggleFace.checked ? '1' : '0',
            tesselation: toggleTesselation.checked ? '1' : '0',
            pose: togglePose.checked ? '1' : '0',
            hands: toggleHands.checked ? '1' : '0',
            analytics: toggleAnalytics.checked ? '1' : '0',
            t: Date.now()
        });
        return `/video_feed?${params.toString()}`;
    }

    // Helper: Update Telemetry UI
    function updateTelemetryUI(data) {
        if (!data) return;

        if (data.fps !== undefined && data.fps !== null) {
            fpsValue.textContent = Number(data.fps).toFixed(1);
        }

        const metrics = data.analytics || {};
        valPosture.textContent = metrics.posture_status || 'Detected';
        valGesture.textContent = metrics.hands_up_status || 'Normal';
        valTorsoTilt.textContent = metrics.torso_inclination !== undefined && metrics.torso_inclination !== null ? `${metrics.torso_inclination}°` : '--°';
        valShoulderTilt.textContent = metrics.shoulder_slope !== undefined && metrics.shoulder_slope !== null ? `${metrics.shoulder_slope}°` : '--°';

        // Update Angles & Progress Bars (Max 180 deg)
        function setAngle(bar, label, val) {
            if (val !== undefined && val !== null) {
                const angle = Number(val);
                label.textContent = `${Math.round(angle)}°`;
                bar.style.width = `${Math.min(100, Math.max(0, (angle / 180) * 100))}%`;
            } else {
                label.textContent = '--°';
                bar.style.width = '0%';
            }
        }

        setAngle(barLeftElbow, degLeftElbow, metrics.left_elbow_angle);
        setAngle(barRightElbow, degRightElbow, metrics.right_elbow_angle);
        setAngle(barLeftKnee, degLeftKnee, metrics.left_knee_angle);
        setAngle(barRightKnee, degRightKnee, metrics.right_knee_angle);

        // Update Counts
        cntFace.textContent = data.face_landmarks_count || 0;
        cntPose.textContent = data.pose_landmarks_count || 0;
        cntLeftHand.textContent = data.left_hand_landmarks_count || 0;
        cntRightHand.textContent = data.right_hand_landmarks_count || 0;

        // Update JSON
        if (!jsonViewer.classList.contains('hidden')) {
            jsonViewer.textContent = JSON.stringify(data, null, 2);
        }
    }

    // Tab Switching
    tabWebcam.addEventListener('click', () => {
        currentMode = 'webcam';
        tabWebcam.classList.add('active');
        tabUpload.classList.remove('active');
        webcamActions.classList.remove('hidden');
        uploadActions.classList.add('hidden');
        uploadedImageResult.classList.add('hidden');
        uploadedVideoResult.classList.add('hidden');

        if (isCameraActive) {
            liveStreamImg.classList.remove('hidden');
            viewportPlaceholder.classList.add('hidden');
        } else {
            liveStreamImg.classList.add('hidden');
            viewportPlaceholder.classList.remove('hidden');
        }
    });

    tabUpload.addEventListener('click', () => {
        currentMode = 'upload';
        tabUpload.classList.add('active');
        tabWebcam.classList.remove('active');
        uploadActions.classList.remove('hidden');
        webcamActions.classList.add('hidden');

        if (isCameraActive) {
            stopCamera();
        }
        liveStreamImg.classList.add('hidden');
    });

    // Start / Stop Camera Stream
    async function startCamera() {
        try {
            const resp = await fetch('/api/camera/start', { method: 'POST' });
            const res = await resp.json();
            if (res.status === 'ok' || res.status === 'already_running') {
                isCameraActive = true;
                liveStreamImg.src = getStreamUrl();
                liveStreamImg.classList.remove('hidden');
                viewportPlaceholder.classList.add('hidden');

                btnToggleCamera.innerHTML = '<i class="fa-solid fa-stop"></i> Stop Camera Stream';
                btnToggleCamera.classList.add('btn-stop');

                cameraStatusBadge.classList.add('active');
                cameraStatusText.textContent = 'Camera Live';

                // Start telemetry poll loop
                if (telemetryInterval) clearInterval(telemetryInterval);
                telemetryInterval = setInterval(async () => {
                    if (!isCameraActive) return;
                    try {
                        const tResp = await fetch('/api/telemetry');
                        const tData = await tResp.json();
                        updateTelemetryUI(tData);
                    } catch (err) {
                        // ignore network glitches
                    }
                }, 200);
            }
        } catch (e) {
            alert('Failed to start camera: ' + e);
        }
    }

    async function stopCamera() {
        try {
            await fetch('/api/camera/stop', { method: 'POST' });
        } catch (e) {}

        isCameraActive = false;
        liveStreamImg.src = '';
        liveStreamImg.classList.add('hidden');
        if (currentMode === 'webcam') {
            viewportPlaceholder.classList.remove('hidden');
        }

        btnToggleCamera.innerHTML = '<i class="fa-solid fa-play"></i> Start Camera Stream';
        btnToggleCamera.classList.remove('btn-stop');

        cameraStatusBadge.classList.remove('active');
        cameraStatusText.textContent = 'Camera Idle';
        fpsValue.textContent = '0.0';

        if (telemetryInterval) {
            clearInterval(telemetryInterval);
            telemetryInterval = null;
        }
    }

    btnToggleCamera.addEventListener('click', () => {
        if (isCameraActive) {
            stopCamera();
        } else {
            startCamera();
        }
    });

    // Handle Layer Toggles Change during live stream
    [toggleFace, toggleTesselation, togglePose, toggleHands, toggleAnalytics].forEach(el => {
        el.addEventListener('change', () => {
            if (isCameraActive) {
                // Refresh stream endpoint with new options
                liveStreamImg.src = getStreamUrl();
            }
        });
    });

    // Save Snapshot
    btnSnapshot.addEventListener('click', () => {
        if (!isCameraActive) {
            alert('Please start camera first.');
            return;
        }
        const a = document.createElement('a');
        a.href = liveStreamImg.src;
        a.download = `holistic_snapshot_${Date.now()}.jpg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });

    // Fullscreen Toggle
    btnFullscreen.addEventListener('click', () => {
        const container = document.getElementById('viewportContainer');
        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(err => alert(err.message));
        } else {
            document.exitFullscreen();
        }
    });

    // Collapsible JSON Inspector
    btnToggleJson.addEventListener('click', () => {
        jsonViewer.classList.toggle('hidden');
        jsonChevron.classList.toggle('fa-chevron-up');
        jsonChevron.classList.toggle('fa-chevron-down');
    });

    // File Upload Handling
    btnBrowseFile.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    async function handleFileUpload(file) {
        const isVideo = file.type.startsWith('video/') || file.name.endsWith('.mp4');
        const formData = new FormData();
        formData.append('file', file);
        formData.append('face', toggleFace.checked ? '1' : '0');
        formData.append('tesselation', toggleTesselation.checked ? '1' : '0');
        formData.append('pose', togglePose.checked ? '1' : '0');
        formData.append('hands', toggleHands.checked ? '1' : '0');
        formData.append('analytics', toggleAnalytics.checked ? '1' : '0');

        loadingSpinner.classList.remove('hidden');
        spinnerText.textContent = isVideo ? 'Processing video frames...' : 'Detecting landmarks...';
        viewportPlaceholder.classList.add('hidden');
        uploadedImageResult.classList.add('hidden');
        uploadedVideoResult.classList.add('hidden');

        try {
            const endpoint = isVideo ? '/api/process_video' : '/api/process_image';
            const resp = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.error || 'Server error');
            }

            const data = await resp.json();

            if (isVideo) {
                uploadedVideoResult.src = data.output_video_url;
                uploadedVideoResult.classList.remove('hidden');
                uploadedVideoResult.play();
            } else {
                uploadedImageResult.src = data.annotated_image_base64;
                uploadedImageResult.classList.remove('hidden');
            }

            updateTelemetryUI(data);
        } catch (err) {
            alert('Upload processing error: ' + err.message);
            viewportPlaceholder.classList.remove('hidden');
        } finally {
            loadingSpinner.classList.add('hidden');
        }
    }
});
