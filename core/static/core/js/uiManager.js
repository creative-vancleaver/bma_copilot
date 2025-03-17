export class UIManager {
    constructor(screenShare) {
        this.cropManager = null;
        this.screenShare = null;
        this.cropDimensions = null;
        // DOM elements
        this.elements = {

            navBar: document.getElementById('navBar'),

            controlPanel: document.getElementById('controlPanel'),
            statusPanel: document.getElementById('statusPanel'),

            shareButton: document.getElementById('shareButton'),
            stopButton: document.getElementById('stopButton'),
            resetCropButton: document.getElementById('resetCrop'),
            previewPane: document.getElementById('previewPane'),
            previewCanvas: document.getElementById('previewCanvas'),
            statusDiv: document.getElementById('status'),
            dimensionsDiv: document.getElementById('dimensions'),

            recordButton: document.getElementById('recordButton'),
            confirmRecordButton: document.getElementById('confirmRecordButton'),
            stopRecordingButton: document.getElementById('stopRecordingButton'),

            cropOverlay: document.querySelector('.crop-overlay'),
            cropBox: document.querySelector('.crop-box'),
            screenContainer: document.getElementById('screenContainer'),
            sharedScreen: document.getElementById('sharedScreen'),
            processingContainer: document.getElementById('processingContainer'),

        };

        this.record = false;

    }

    setCropManager(cropManger) {
        this.cropManager = cropManger;
    }

    setScreenShare(screenShare) {
        this.screenShare = screenShare;
    }

    initialize(screenShare, cropManager) {
        // Any initial UI setup

        this.elements.recordButton.addEventListener("click", () => {
            screenShare.enableDrawing();
            cropManager.enableDrawing();
            this.showConfirmRecordButton();
        });

        this.elements.stopRecordingButton.addEventListener("click", () => {
            screenShare.stopRecording();
            screenShare.stopSharing();
        });

        this.elements.confirmRecordButton.addEventListener("click", () => {
            screenShare.startRecording();
            this.toggleRecordButton();
            this.openPreviewWindow();
        });

        this.elements.stopButton.addEventListener("click", () => {
            screenContainer.style.display = 'none';
            screenShare.stopRecording();
            screenShare.stopSharing();
            this.resetDisplay();
        });
    }

    openPreviewWindow() {
        const previewCanvas = document.getElementById("previewCanvas");
        if (!previewCanvas) {
            alert("No preview available!");
            return;
        }
    
        // Get the cropBox dimensions
        const cropBox = document.querySelector(".crop-box");
        if (!cropBox) {
            alert("Crop box not found!");
            return;
        }
    
        const cropBoxRect = cropBox.getBoundingClientRect();
        const parentWidth = window.innerWidth;
        const parentHeight = window.innerHeight;
    
        // Set padding around the video
        const padding = 40; // Adjust for margin around the video
    
        // Get true resolution with high pixel density
        const pixelRatio = window.devicePixelRatio || 1;
    
        let cropWidth = cropBoxRect.width * pixelRatio;
        let cropHeight = cropBoxRect.height * pixelRatio;
    
        // Ensure the preview fits within the available screen size
        const maxPreviewWidth = parentWidth - padding * 2;
        const maxPreviewHeight = parentHeight - padding * 2 - 60; // Extra for button
    
        // Scale down if needed to fit within the preview window
        const scaleFactor = Math.min(1, maxPreviewWidth / cropWidth, maxPreviewHeight / cropHeight);
    
        cropWidth *= scaleFactor;
        cropHeight *= scaleFactor;
    
        // Calculate preview window size
        const windowWidth = cropWidth + padding * 2;
        const windowHeight = cropHeight + padding * 2 + 60; // Extra for button
    
        // Center the preview window
        const left = window.screenX + (window.outerWidth - windowWidth) / 2;
        const top = window.screenY + (window.outerHeight - windowHeight) / 2;
    
        const previewWindow = window.open("", "CroppedLivePreview", 
            `width=${windowWidth},height=${windowHeight},left=${left},top=${top},resizable=no`);
    
        if (!previewWindow) {
            this.updateStatus('Pop-ups are blocked. Please allow popups for this site.');
            return;
        }
    
        previewWindow.document.write(`
            <html>
            <head>
                <title>Live Preview</title>
                <style>
                    body {
                        margin: 0;
                        background: black;
                        color: white;
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        flex-direction: column;
                        height: 100vh;
                        overflow: hidden;
                    }
                    .preview-container {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        width: 100%;
                        height: 100%;
                        padding: ${padding}px;
                    }
                    .canvas-wrapper {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        width: ${cropWidth}px;
                        height: ${cropHeight}px;
                        background-color: #222;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
                    }
                    canvas {
                        width: 100%;
                        height: 100%;
                        image-rendering: pixelated;
                    }
                    .button-wrapper {
                        text-align: center;
                        margin-top: 15px;
                    }
                    .btn-stop {
                        padding: 12px 24px;
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        transition: background 0.2s;
                    }
                    .btn-stop:hover {
                        background-color: #c82333;
                    }
                </style>
            </head>
            <body>
                <div class="preview-container">
                    <div class="canvas-wrapper">
                        <canvas id="mirroredCanvas"></canvas>
                    </div>
                    <div class="button-wrapper">
                        <button class="btn-stop" id="stopRecordingButton">Stop Recording</button>
                    </div>
                </div>
            </body>
            </html>
        `);
    
        previewWindow.document.close();
        this.previewWindow = previewWindow;
        previewWindow.focus();
    
        previewWindow.onload = () => {
            const mirroredCanvas = previewWindow.document.getElementById('mirroredCanvas');
            const mirroredCtx = mirroredCanvas.getContext('2d', { willReadFrequently: true });
    
            // **High DPI Scaling**
            mirroredCanvas.width = cropWidth * pixelRatio;
            mirroredCanvas.height = cropHeight * pixelRatio;
            mirroredCanvas.style.width = `${cropWidth}px`;
            mirroredCanvas.style.height = `${cropHeight}px`;
    
            // **Disable Smoothing for Pixel-Perfect Quality**
            mirroredCtx.imageSmoothingEnabled = false;
    
            // **Use an Offscreen Canvas for High-Quality Rendering**
            const offscreenCanvas = document.createElement('canvas');
            const offscreenCtx = offscreenCanvas.getContext('2d');
    
            offscreenCanvas.width = previewCanvas.width * pixelRatio;
            offscreenCanvas.height = previewCanvas.height * pixelRatio;
    
            const updatePreview = () => {
                if (!previewCanvas) return;
    
                // Copy to offscreen canvas at full resolution
                offscreenCtx.clearRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);
                offscreenCtx.drawImage(previewCanvas, 0, 0, offscreenCanvas.width, offscreenCanvas.height);
    
                // Copy to mirrored canvas, scaling it down smoothly
                mirroredCtx.clearRect(0, 0, mirroredCanvas.width, mirroredCanvas.height);
                mirroredCtx.drawImage(offscreenCanvas, 0, 0, mirroredCanvas.width, mirroredCanvas.height);
    
                requestAnimationFrame(updatePreview);
            };
    
            updatePreview();
        };
    
        // Stop button listener
        previewWindow.document.getElementById('stopRecordingButton').addEventListener('click', () => {
            this.elements.stopRecordingButton.click();
            previewWindow.close();
            window.focus();
        });
    
        // Ensure window close stops recording
        previewWindow.onbeforeunload = () => {
            this.elements.stopRecordingButton.click();
            window.focus();
        };
    }
    

    scrollToElement(element) {

        if (!element) return 0;

        const navbarHeight = this.elements.navBar.offsetHeight;
        const rect = element.getBoundingClientRect();

        const computedStyle = window.getComputedStyle(element);
        const marginTop = parseFloat(computedStyle.marginTop) || 0;
        const paddingTop = parseFloat(computedStyle.paddingTop) || 0;

        return rect.top + window.scrollY - navbarHeight - marginTop - paddingTop;

    }

    showConfirmRecordButton() {
        this.elements.confirmRecordButton.style.display = "inline-block";
        // Ensure button starts disabled
        this.updateConfirmRecordButton(false);
        this.elements.recordButton.style.display = 'none';
        this.updateStatus("Please select a preview area.");
    }

    updateConfirmRecordButton(enable = false) {
        this.elements.confirmRecordButton.disabled = !enable;
        this.elements.confirmRecordButton.style.cursor = enable ? 'pointer' : 'not-allowed';
        this.elements.confirmRecordButton.style.opacity = enable ? 1 : 0.5;
    }

    lockToPreviewArea() {

        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth"
        });
    
        this.elements.stopRecordingButton.style.display = 'block';
        this.updateStatus('Recroding started. Viewing limitted to viewing area.');
    }

    toggleRecordButton() {
        this.elements.confirmRecordButton.style.display = "none";
        this.recording = true;
    }

    resetDisplay() {
        this.elements.cropOverlay.style.border = "none";
        this.elements.confirmRecordButton.style.display = "none";
        this.recording = false;
        this.updateStatus('Recording stopped');
    }

    updateStatus(message, statusType) {
        // this.elements.statusDiv.textCinontent = message;
        this.elements.statusDiv.innerHTML = message;
        if (statusType) {
            this.elements.statusDiv.classList.add(statusType);
        }
    }

    updateDimensions(trueWidth, trueHeight, cropWidth, cropHeight, scale) {
        this.elements.dimensionsDiv.textContent = 
            `Source: ${trueWidth}x${trueHeight} | Crop: ${cropWidth}x${cropHeight} | Scale: ${scale.toFixed(2)}x`;
    }

    toggleButtons(isSharing) {
        this.elements.shareButton.style.display = isSharing ? 'none' : 'inline-block';
        this.elements.stopButton.style.display = isSharing ? 'inline-block' : 'none';
    }

    getElements() {
        return this.elements;
    }

    videoCropDimensions(dimensions) {
        if (dimensions) {
            this.cropDimensions = dimensions;
        }
        return this.cropDimensions;
    }
}