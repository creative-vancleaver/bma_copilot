export class ScreenShare {

    constructor(uiManager) {

        this.uiManager = uiManager;
        this.elements = uiManager.getElements();

        // Core properties
        this.stream = null;

        this.recorder = null;
        this.recordedChunks = null;

        this.trueWidth = 0;
        this.trueHeight = 0;
        this.isDrawing = false;
        this.startX = 0;
        this.startY = 0;
        this.currentX = 0;
        this.currentY = 0;

        this.ctx = this.elements.previewCanvas.getContext('2d');

        // Bind methods
        this.startDraw = this.startDraw.bind(this);
        this.draw = this.draw.bind(this);
        this.endDraw = this.endDraw.bind(this);
        this.updatePreview = this.updatePreview.bind(this);
        this.startScreenShare = this.startScreenShare.bind(this);
        this.stopSharing = this.stopSharing.bind(this);
        this.resetCrop = this.resetCrop.bind(this);
    }

    getTrueWidth() {
        return this.trueWidth;
    }

    getTrueHeight() {
        return this.trueHeight;
    }

    initializeEventListeners() {
        const { cropOverlay, shareButton, stopButton, resetCropButton } = this.elements;

        cropOverlay.addEventListener('mousedown', this.startDraw);
        cropOverlay.addEventListener('mousemove', this.draw);
        cropOverlay.addEventListener('mouseup', this.endDraw);
        cropOverlay.addEventListener('mouseleave', this.endDraw);
        shareButton.addEventListener('click', this.startScreenShare);
        stopButton.addEventListener('click', this.stopSharing);
        resetCropButton.addEventListener('click', this.resetCrop);
    }

    updateStatus(message) {
        console.log(message);
        this.elements.statusDiv.textContent = message;
    }

    updateDimensions() {
        const { sharedScreen, dimensionsDiv, previewCanvas } = this.elements;
        const width = Math.abs(this.currentX - this.startX);
        const height = Math.abs(this.currentY - this.startY);
        const bounds = sharedScreen.getBoundingClientRect();
        const scale = this.trueWidth / bounds.width;
        const trueBoxWidth = Math.round(width * scale);
        const trueBoxHeight = Math.round(height * scale);

        dimensionsDiv.textContent = `Source: ${this.trueWidth}x${this.trueHeight} | Crop: ${trueBoxWidth}x${trueBoxHeight} | Scale: ${scale.toFixed(2)}x`;

        previewCanvas.width = trueBoxWidth;
        previewCanvas.height = trueBoxHeight;
    }

    startDraw(e) {
        const { cropOverlay, cropBox, resetCropButton } = this.elements;
        this.isDrawing = true;
        const bounds = cropOverlay.getBoundingClientRect();
        this.startX = e.clientX - bounds.left;
        this.startY = e.clientY - bounds.top;
        cropBox.style.display = 'block';
        resetCropButton.style.display = 'inline-block';
    }

    draw(e) {
        if (!this.isDrawing) return;

        const { cropOverlay, cropBox } = this.elements;
        const bounds = cropOverlay.getBoundingClientRect();
        this.currentX = Math.min(Math.max(e.clientX - bounds.left, 0), bounds.width);
        this.currentY = Math.min(Math.max(e.clientY - bounds.top, 0), bounds.height);

        const left = Math.min(this.startX, this.currentX);
        const top = Math.min(this.startY, this.currentY);
        const width = Math.abs(this.currentX - this.startX);
        const height = Math.abs(this.currentY - this.startY);

        cropBox.style.left = left + 'px';
        cropBox.style.top = top + 'px';
        cropBox.style.width = width + 'px';
        cropBox.style.height = height + 'px';

        this.updateDimensions();
    }

    getVideoBounds() {
        if (!this.elements.sharedScreen) {
            console.error('sharedScreen element is missing');
            return { width: 0, height: 0}
        }

        return this.elements.sharedScreen.getBoundingClientRect()
    }

    endDraw() {
        this.isDrawing = false;
    }

    resetCrop() {
        const { cropBox, resetCropButton, previewCanvas, dimensionsDiv } = this.elements;
        cropBox.style.display = 'none';
        resetCropButton.style.display = 'none';
        this.ctx.clearRect(0, 0, previewCanvas.width, previewCanvas.height);
        dimensionsDiv.textContent = `Source: ${this.trueWidth}x${this.trueHeight} | Crop: Not Selected`;
        
        const recordingIndicator = document.getElementById('recordingIndicator');
        recordingIndicator.classList.remove('live');
        recordingIndicator.classList.add('active');
        
        this.updateStatus('Selection cleared - Click and drag again to select a new region');
    }

    async startScreenShare() {
        const { sharedScreen, cropOverlay, shareButton, stopButton, recordButton, controlPanel, navBar, statusPanel } = this.elements;

        this.updateStatus('Click "Start Screen Share" and select the window or screen you want to share');

        try {

            if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
                throw new Error('Screen sharing is not supported in this browser');
            }

            // if (navigator.mediaDevices.setCaptureHandleConfig) {
            //     navigator.mediaDevices.setCaptureHandleConfig({
            //         excludedElements: [document.getElementById("previewModal")]
            //     });
            // }

            console.log('attempting screen share ', this);

            // START SCREEN SHARING
            this.stream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    cursor: "never",
                    // displaySurface: "monitor",
                    displaySurface: "window",
                    // displaySurface: 'browser',
                },
                audio: false
            });

            console.log("screen share started successfully!", this.stream);

            const hiddenScreenRecorder = document.getElementById("hiddenScreenRecorder");
            sharedScreen.srcObject = this.stream;
            // this.uiManager.elements.previewVideo.srcObject = this.stream;
            // previewVideo.srcObject = this.stream;
            hiddenScreenRecorder.srcObject = this.stream;

            recordButton.style.display = "inline-block";

            await new Promise(resolve => {
                sharedScreen.onloadedmetadata = () => {
                    this.trueWidth = sharedScreen.videoWidth;
                    this.trueHeight = sharedScreen.videoHeight;
                    resolve();
                };
            });

            await sharedScreen.play();

            // await new Promise(resolve => {
            //     previewVideo.onloadedmetadata = () => {
            //         this.trueWidth = previewVideo.videoWidth;
            //         this.trueHeight = previewVideo.videoHeight;
            //         resolve();
            //     };
            // });
    
            // await previewVideo.play();
    

            this.uiManager.updateStatus("Screen sharing started. Click and drag to select a preview area.");
            shareButton.style.display = "none";
            // stopButton.style.display = "inline-block";
            recordButton.style.display = "inline-block";

            const recordingIndicator = document.getElementById('recordingIndicator');
            recordingIndicator.classList.add('active');
            this.updateStatus('Please drag to draw a box to crop the view region you want the AI to examine');
            this.updateDimensions();

            sharedScreen.style.display = 'block';
            cropOverlay.style.display = 'block';
            stopButton.style.display = 'inline-block';

            const navHeight = navBar.offsetHeight;
            console.log('navHeight ', navHeight);
            const position = statusPanel.getBoundingClientRect().top + window.scrollY;
            const offsetPosition = position - navHeight;
            console.log('offset ', offsetPosition);
            window.scrollTo({ behavior: "smooth", top: offsetPosition });

            // START RECORDING ENTIRE SCREEN
            // this.startRecording(this.stream);

            // this.uiManager.elements.previewVideo.play();

            this.stream.getVideoTracks()[0].addEventListener('ended', () => {
                this.uiManager.updateStatus("Screen share stopped by user.")
                this.updateStatus('Screen share stopped by user');
                this.stopSharing();
            });

            requestAnimationFrame(this.updatePreview);

            // *** REPLACED WITH RECORDING ABOVE ***
            // Start automatic screenshots every 10 seconds
            // this.screenshotInterval = setInterval(() => {
            //     this.captureAndSendScreenshot();
            // }, 2000);

        } catch (err) {
            this.updateStatus(`Error: ${err.message}`);
            console.error("Screen share error:", err);
            this.stopSharing();
        }
    }

    startRecording() {

        this.recordedChunks = [];
        const hiddenScreenRecorder = document.getElementById("hiddenScreenRecorder");

        if (!hiddenScreenRecorder || !hiddenScreenRecorder.srcObject) {
            console.log('Error: No valid screen recording source')
            return;
        }

        // this.recorder = new MediaRecorder(hiddenScreenRecorder.srcObject, { mimeType: "video/webm" });
        this.recorder = new MediaRecorder(this.stream, { mimeType: "video/webm" });

        this.recorder.ondataavailable = event => {
            if (event.data.size > 0) {
                this.recordedChunks.push(event.data);
            }
        };

        this.recorder.onstop = () => {
            this.saveRecording();
        };

        this.recorder.start();
        this.uiManager.updateStatus('Recording in progress...');

    }

    stopRecording() {
        
        if (this.recorder) {
            this.recorder.stop();
            this.uiManager.updateStatus('Recording stopped.');
            this.recorder = null;
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
        this.uiManager.elements.stopRecordingButton.style.display = 'none';

        // this.uiManager.closePreviewModal();

    }

    saveRecording() {

        const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
        const formData = new FormData();
        formData.append("video", blob, 'screen-recording.webm');

        // TEST CASE
        let case_id = 1;

        fetch(`/api/cases/${ case_id }/save-recording/`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.uiManager.updateStatus(`Recording saved.`);
            } else {
                console.error('Upload failed: ', data.error);
            }
        })
        .catch(error => console.log('Upload error: ', error));
        // const url = URL.createObjectURL(blob);
        // const a = document.createElement('a');

        // a.href = url;
        // a.download = 'screen-recording.webm';
        // document.body.appendChild(a);
        // a.click();
        // URL.revokeObjectURL(url);
        // this.uiManager.updateDimensions('Recording saveded.');

    }

    stopSharing() {
        const { sharedScreen, cropOverlay, cropBox, shareButton, 
            stopButton, resetCropButton, previewCanvas, recordButton, confirmRecordButton } = this.elements;

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            if (this.screenshotInterval) {
                clearInterval(this.screenshotInterval);
                this.screenshotInterval = null;
            }
        }

        // STOP RECORDING WHEN SHARING ENDS
        this.stopRecording();
        
        // Remove active class from recording indicator and status
        const recordingIndicator = document.getElementById('recordingIndicator');
        recordingIndicator.classList.remove('active');
        recordingIndicator.classList.remove('live');
        
        previewCanvas.style.display = 'none';
        sharedScreen.srcObject = null;
        sharedScreen.style.display = 'none';
        cropOverlay.style.display = 'none';
        cropBox.style.display = 'none';
        shareButton.style.display = 'inline-block';
        stopButton.style.display = 'none';
        resetCropButton.style.display = 'none';

        recordButton.style.display = 'none';
        confirmRecordButton.style.display = 'none';

        this.updateStatus('Screen capture ended');
        this.elements.dimensionsDiv.textContent = 'Resolution: Not sharing';

        this.ctx.clearRect(0, 0, previewCanvas.width, previewCanvas.height);
    }

    updatePreview() {
        const { sharedScreen, cropBox, previewCanvas } = this.elements;

        if (!this.stream || cropBox.style.display === 'none') {
            requestAnimationFrame(this.updatePreview);
            return;
        }

        try {
            const bounds = sharedScreen.getBoundingClientRect();
            const scale = this.trueWidth / bounds.width;

            const left = Math.min(this.startX, this.currentX);
            const top = Math.min(this.startY, this.currentY);
            const width = Math.abs(this.currentX - this.startX);
            const height = Math.abs(this.currentY - this.startY);

            const trueX = left * scale;
            const trueY = top * scale;
            const trueBoxWidth = width * scale;
            const trueBoxHeight = height * scale;

            previewCanvas.width = trueBoxWidth;
            previewCanvas.height = trueBoxHeight;

            this.ctx.drawImage(
                sharedScreen,
                trueX,
                trueY,
                trueBoxWidth,
                trueBoxHeight,
                0,
                0,
                previewCanvas.width,
                previewCanvas.height
            );

            requestAnimationFrame(this.updatePreview);
        } catch (error) {
            console.error('Error in updatePreview:', error);
            requestAnimationFrame(this.updatePreview);
        }
    }

    async captureAndSendScreenshot() {
        if (!this.stream || this.elements.cropBox.style.display === 'none') {
            return;
        }

        const canvas = document.createElement('canvas');
        const bounds = this.elements.sharedScreen.getBoundingClientRect();
        const scale = this.trueWidth / bounds.width;

        const left = Math.min(this.startX, this.currentX);
        const top = Math.min(this.startY, this.currentY);
        const width = Math.abs(this.currentX - this.startX);
        const height = Math.abs(this.currentY - this.startY);

        const trueX = left * scale;
        const trueY = top * scale;
        const trueBoxWidth = width * scale;
        const trueBoxHeight = height * scale;

        canvas.width = trueBoxWidth;
        canvas.height = trueBoxHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(
            this.elements.sharedScreen,
            trueX,
            trueY,
            trueBoxWidth,
            trueBoxHeight,
            0,
            0,
            canvas.width,
            canvas.height
        );

        // Convert to base64
        const base64Image = canvas.toDataURL('image/jpeg');

        try {

            let caseID = 1;

            const formData = new URLSearchParams();
            formData.append("image", base64Image);

            const response = await fetch(`/api/cases/${ caseID }/save-screenshot/`, {
                method: 'POST',
                headers: {
                    // 'Content-Type': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                // body: JSON.stringify({ image: base64Image })
                body: formData
            });
            const result = await response.json();
            console.log('RESPONSE = ', result);
            if (result.success) {
                const recordingIndicator = document.getElementById('recordingIndicator');
                recordingIndicator.classList.remove('active');
                recordingIndicator.classList.add('live');
                this.updateStatus('Screen capture live');
            } else {
                console.error('Failed to save screenshot:', result.error);
            }
        } catch (error) {
            console.error('Error sending screenshot:', error);
        }
    }

    initialize() {
        this.initializeEventListeners();
        this.updateStatus('Ready to share screen');
    }
}