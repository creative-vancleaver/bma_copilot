export class UIManager {
    constructor(screenShare) {
        // this.cropManager = cropManager;
        this.screenShare = screenShare;
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
            // previewModal: document.getElementById('previewModal'),
            // previewVideo: document.getElementById('previewVideo'),
            cropOverlay: document.querySelector('.crop-overlay'),
            cropBox: document.querySelector('.crop-box'),
            sharedScreen: document.getElementById('sharedScreen'),
            // hiddenScreenRecorder: document.getElementById('hiddenScreenRecorder'),

        };

        this.record = false;

    }

    initialize(screenShare, cropManager) {
        // Any initial UI setup

        this.elements.recordButton.addEventListener("click", () => {
            this.showConfirmRecordButton();
        });

        this.elements.stopRecordingButton.addEventListener("click", () => {
            screenShare.stopRecording();
            screenShare.stopSharing();
        });

        this.elements.confirmRecordButton.addEventListener("click", () => {
            screenShare.startRecording();
            this.lockToPreviewArea();
            this.toggleRecordButton();
        });

        this.elements.stopButton.addEventListener("click", () => {
            screenShare.stopRecording();
            screenShare.stopSharing();
            this.resetDisplay();
        });
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
        // DISABLE BUTTON UNTIL AFTER SELECTION IS MADE
        this.elements.confirmRecordButton.disabled = true;
        this.elements.confirmRecordButton.style.cursor = 'not-allowed';
        this.elements.confirmRecordButton.style.opacity = 0.5;
        this.elements.recordButton.style.display = 'none';
        this.updateStatus("Please select a preview area.");
    }

    updateConfirmRecordButton() {
        this.elements.confirmRecordButton.style.cursor = 'pointer';
        this.elements.confirmRecordButton.style.opacity = 1;
        this.elements.confirmRecordButton.disabled = false;
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

    updateStatus(message) {
        this.elements.statusDiv.textContent = message;
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
}