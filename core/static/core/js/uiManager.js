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
 
        // CALCULATE WINDOW SIZE BASED ON CONTENT
        // const headerHeight = 100;
        // const buttonHeight = 50;
        // const padding = 80;
        // const paddingBottom = 80;
        
        // const windowWidth = previewCanvas.width + padding;
        // const windowHeight = previewCanvas.height + headerHeight + buttonHeight + padding + paddingBottom;

        const windowWidth = previewCanvas.width + 100;
        const windowHeight = previewCanvas.height + 100;
        
        // CALCULATE WINDOW CENTER BASED ON PARENT ELEMENT
        const parentLeft = window.screenX;
        const parentTop = window.screenY;
        const parentWidth = window.outerWidth;
        const parentHeight = window.outerHeight;

        // CALCULATE CENTER POSITION
        const left = parentLeft + (parentWidth - windowWidth) / 2;
        const top = parentTop + (parentHeight - windowHeight) / 2;
        
        const previewWindow = window.open("", "CroppedLivePreview", 
            `width=${windowWidth},height=${windowHeight},left=${left},top=${top}`);

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
                        padding: 20px;
                        display: flex;
                        flex-direction: column;
                        background: black;
                        color: white;
                        font-family: Arial, sans-serif;
                        height: ${previewCanvas.height}px;
                        box-sizing: border-box;
                    }
                    .preview-container {
                        display: flex;
                        flex-direction: column;
                        height: 80%;
                        overflow: hidden;
                    }
                    .preview-header {
                        text-align: center;
                        flex: 0 0 auto;
                        margin-bottom: 10px;
                    }
                    h3 {
                        margin: 0 0 5px 0;
                        font-size: 16px;
                    }
                    .preview-subtitle {
                        color: #999;
                        font-size: 12px;
                        display: block;
                    }
                    .canvas-wrapper {
                        flex: 1 1 auto;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    canvas { 
                        display: block;
                        width: ${previewCanvas.width}px;
                        height: ${previewCanvas.height}px;
                        image-rendering: -webkit-optimize-contrast;
                        image-rendering: crisp-edges;
                        image-rendering: pixelated;
                    }
                    .button-wrapper {
                        flex: 0 0 auto;
                        text-align: center;
                        margin-top: 10px;
                    }
                    .btn-stop {
                        padding: 8px 16px;
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 14px;
                    }
                    .btn-stop:hover {
                        background-color: #c82333;
                    }
                </style>
            </head>
            <body>
                <div class="preview-container">
                    <div class="preview-header">
                        <h3>Live Preview</h3>
                        <span class="preview-subtitle">Real-time view of captured whole slide image regions</span>
                    </div>
                    <div class="canvas-wrapper">
                        <canvas id="mirroredCanvas"></canvas>
                    </div>

                </div>
                <div class="button-wrapper">
                    <button class="btn-stop" id="stopRecordingButton">
                        Stop Recording
                    </button>
                </div>
            </body>
            </html>
        `);

        previewWindow.document.close();
        this.previewWindow = previewWindow;

        // BRING TO FRONT (FOCUS)
        previewWindow.focus();

        // WAIT FOR WINDOW TO LOAD
        previewWindow.onload = () => {

            const mirroredCanvas = previewWindow.document.getElementById('mirroredCanvas');
            const mirroredCtx = mirroredCanvas.getContext('2d');

            // MATCH CANVAS SIZE TO ORIGINAL PREVIEW CANVAS
            mirroredCanvas.width = previewCanvas.width;
            mirroredCanvas.height = previewCanvas.height;

            const updatePreview = () => {
                if (!previewCanvas) return;
                mirroredCtx.clearRect(0, 0, mirroredCanvas.width, mirroredCanvas.height);
                mirroredCtx.drawImage(previewCanvas, 0, 0, mirroredCanvas.width, mirroredCanvas.height);
                requestAnimationFrame(updatePreview);
            }

            updatePreview();

        };

        // ADD EVENT LISTENER FOR STOP RECORDING BUTTON
        previewWindow.document.getElementById('stopRecordingButton').addEventListener('click', () => {
            this.elements.stopRecordingButton.click();
            previewWindow.close();
            screenContainer.style.display = 'none';
            // BRING MAIN WINDOW BACK TO FOCUS
            window.focus();
        });

        // ADD WINDOW CLOSE HANDLER
        previewWindow.onbeforeunload = () => {
            this.elements.stopRecordingButton.click();
            window.focus();
        };

        previewWindow.focus();
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