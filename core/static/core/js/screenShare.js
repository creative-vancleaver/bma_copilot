import { uploadState, updateProgressBar, processingState, checkVideoStatus } from './uploadState.js';

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
        this.canDraw = false,
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
        const { cropOverlay, shareButton, stopButton, resetCropButton, processingContainer } = this.elements;

        cropOverlay.addEventListener('mousedown', this.startDraw);
        cropOverlay.addEventListener('mousemove', this.draw);
        cropOverlay.addEventListener('mouseup', this.endDraw);
        // cropOverlay.addEventListener('mouseleave', this.endDraw);
        // shareButton.addEventListener('click', this.startScreenShare);
        shareButton.addEventListener('click', () => {
            processingContainer.style.display = 'none';
            this.startScreenShare();
        })
        stopButton.addEventListener('click', this.stopSharing);
        resetCropButton.addEventListener('click', this.resetCrop);
    }

    updateStatus(message, statusType) {
        this.elements.statusDiv.innerHTML = message;
        // REMOVE PREVIOUS STATUS CLASSES
        this.elements.statusDiv.classList.remove("ready", "initialize", "recording");
        if (statusType) {
            this.elements.statusDiv.classList.add(statusType);
        }
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

    enableDrawing() {
        this.canDraw = true;
        document.querySelector('.crop-overlay').style.cursor = 'crosshair';
    }

    disableDrawing() {
        this.canDraw = false;
    }

    startDraw(e) {
        
        if (!this.canDraw) return;

        const { cropOverlay, cropBox, resetCropButton } = this.elements;
        this.isDrawing = true;
        const bounds = cropOverlay.getBoundingClientRect();
        this.startX = e.clientX - bounds.left;
        this.startY = e.clientY - bounds.top;
        cropBox.style.display = 'block';
        resetCropButton.style.display = 'inline-block';
    }

    draw(e) {
        if (!this.canDraw || !this.isDrawing) return;

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
        this.uiManager.updateConfirmRecordButton(false);  // Disable confirm button on reset
        
        this.updateStatus('Selection cleared - Click and drag again to select a new region');
    }

    async startScreenShare() {
        const { processingContainer, screenContainer, sharedScreen, cropOverlay, shareButton, stopButton, recordButton, controlPanel, navBar, statusPanel } = this.elements;

        this.updateStatus(`Confirm screen sharing in your browser and select the window or screen you want to share.`);

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

            screenContainer.style.display = 'inline-block';

            sharedScreen.srcObject = this.stream;
            // document.getElementById('screen-share-overlay').remove();

            recordButton.style.display = "inline-block";

            await new Promise(resolve => {
                sharedScreen.onloadedmetadata = () => {
                    this.trueWidth = sharedScreen.videoWidth;
                    this.trueHeight = sharedScreen.videoHeight;
                    resolve();
                };
            });

            await sharedScreen.play();    

            // this.uiManager.updateStatus("Screen sharing started. Click and drag to select a preview area.");
            processingContainer.style.display = 'none';
            shareButton.style.display = "none";
            recordButton.style.display = "inline-block";
            document.getElementById('mainContent').style.minHeight = '130vh';

            const recordingIndicator = document.getElementById('recordingIndicator');
            recordingIndicator.classList.add('active');
            let message = `Select <span>Crop Region</span> then click and drag to crop the region you want the AI to examine.`;
            let statusType = 'active';
            this.updateStatus(message, statusType);
            this.updateDimensions();

            sharedScreen.style.display = 'block';
            cropOverlay.style.display = 'block';
            stopButton.style.display = 'inline-block';

            const navHeight = navBar.offsetHeight;
            const position = statusPanel.getBoundingClientRect().top + window.scrollY;
            const offsetPosition = position - navHeight;
            window.scrollTo({ behavior: "smooth", top: offsetPosition });

            // START RECORDING ENTIRE SCREEN
            // this.startRecording(this.stream);

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

        if (this.uiManager.previewWindow && !this.uiManager.previewWindow.closed) {
            this.uiManager.previewWindow.close();
        }

        if (this.recorder) {
            this.recorder.stop();
            this.uiManager.updateStatus('Recording stopped.');
            this.recorder = null;
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
        this.uiManager.elements.stopRecordingButton.style.display = 'none';
        document.getElementById('mainContent').style.minHeight = '50vh';        

    }

    async saveRecording() {

        const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
        const formData = new FormData();
        formData.append("video", blob, 'screen-recording.webm');

        // GET CROPPED REGION DIMENSIONS
        const cropDimensions = this.uiManager.cropManager.NEWgetCropDimensions();
        console.log('cropDimensions ', cropDimensions)
        const cropData = {
            TL_x: cropDimensions.left,
            TL_y: cropDimensions.top,
            BR_x: cropDimensions.left + cropDimensions.width,
            BR_y: cropDimensions.top + cropDimensions.height
        };
        formData.append('crop_data', JSON.stringify(cropData))
        console.log('formData ', formData)

        // RESET UPLOAD STATE
        uploadState.progress = 0;
        uploadState.status = 'uploading';
        uploadState.error = null;
        updateProgressBar();

        try {

            // SEND REQUEST TO UPLOAD VIDEO
            const response = await fetch(`/api/cases/save-recording/`, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFTOken': ScreenShare.getCSRFToken() }
            });

            if (!response.ok) {
                throw new Error(`Server Error: ${ response.status }`);
            }

            const result = await response.json();
            if (result.success) {
                uploadState.status = 'completed';
                updateProgressBar();

                // START CHECKING VIDEO PROCESSING STATUS
                // checkVideoStatus(result.video_id);

            } else {
                throw new Error(result.error || 'Upload failed.');
            }

        } catch (error) {

            uploadState.status = 'error';
            uploadState.error = error.message;
            console.log('upload error: ', error);

        } finally {
            updateProgressBar();
        }
    }


    // saveRecording() {

    //     const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
    //     const formData = new FormData();
    //     formData.append("video", blob, 'screen-recording.webm');

    //     // RESET UPLOAD STATE
    //     uploadState.progress = 0;
    //     uploadState.status = 'uploading';
    //     uploadState.error = null;
    //     updateProgressBar();

    //     // TEST CASE
    //     // let case_id = 1;

    //     const xhr = new XMLHttpRequest();
    //     xhr.open('POST', `/api/cases/save-recording/`, true);

    //     xhr.setRequestHeader('X-CSRFToken', ScreenShare.getCSRFToken());

    //     xhr.upload.onprogress = (event) => {
    //         if (event.lengthComputable) {
    //             const percentComplete = Math.round((event.loaded / event.total) * 100);
    //             uploadState.progress = percentComplete;
    //             updateProgressBar();
    //         }
    //     };

    //     xhr.onload = () => {
    //         if (xhr.status === 200) {
    //             const response = JSON.parse(xhr.responseText);
    //             if (response.success) {
    //                 // Mark upload as completed
    //                 uploadState.status = 'completed';
    //                 uploadState.progress = 100;
    //                 updateProgressBar();
                    
    //                 // Hide screen container
    //                 this.elements.screenContainer.style.display = 'none';
                    
    //                 // Show processing container with explicit styles
    //                 // const processingContainer = document.getElementById('processingContainer');
    //                 // processingContainer.style.display = 'flex'; // Use flex instead of block
    //                 // processingContainer.style.position = 'relative';
    //                 // processingContainer.style.width = '100%';
    //                 // // processingContainer.style.height = '100%';
    //                 // processingContainer.style.justifyContent = 'center';
    //                 // processingContainer.style.alignItems = 'center';
    //                 // processingContainer.style.zIndex = '1000'; // Ensure it's above other elements
                    
    //                 // Start processing simulation after a short delay
    //                 // setTimeout(() => {
    //                 //     this.simulateProcessing();
    //                 // }, 1500);
                    
    //             } else {
    //                 uploadState.status = 'error';
    //                 uploadState.error = response.error || 'Upload failed.';
    //                 console.error('Upload failed: ', response.error);
    //             }
    //         } else {
    //             uploadState.status = 'error';
    //             uploadState.error = 'Server Error';
    //             console.error('upload failed: server returned status ', xhr.status);
    //         }
    //         updateProgressBar();
    //     };

    //     xhr.onerror = () => {
    //         uploadState.status = 'error';
    //         uploadState.error = 'Network Error';
    //         updateProgressBar();
    //         console.error('Upload error: network failure.');
    //     };

    //     xhr.send(formData);

    // }

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
        // setTimeout(() => {
        //     let message = `Ready to share screen. Click <span>Start Screen Share</span> to begin!`;
        //     let statusType = 'initialize';
        //     this.updateStatus(message, statusType);
        // }, 15000);
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

    simulateProcessing() {
        const intervals = [
            {
                duration: 10000,
                message: "Analyzing microscope feed...",
                progress: 25
            },
            {
                duration: 10000,
                message: "Detecting cell boundaries...",
                progress: 50
            },
            {
                duration: 10000,
                message: "Classifying cell types...",
                progress: 75
            },
            {
                duration: 10000,
                message: "Generating final report...",
                progress: 100
            }
        ];

        let currentInterval = 0;

        const processNextInterval = () => {
            if (currentInterval >= intervals.length) {
                // Processing complete
                processingState.status = 'completed';
                updateProgressBar();
                // Redirect after a short delay
                setTimeout(() => {
                    window.location.href = '/case/1/';
                }, 1000);
                return;
            }

            const interval = intervals[currentInterval];
            
            // Update processing state
            processingState.status = 'processing';
            processingState.progress = interval.progress;
            processingState.message = interval.message;
            updateProgressBar();

            // Schedule next interval
            setTimeout(() => {
                currentInterval++;
                processNextInterval();
            }, interval.duration);
        };

        // Start processing
        processingState.status = 'processing';
        processingState.progress = 0;
        processNextInterval();
    }

    initialize() {
        this.initializeEventListeners();
        let message = `Ready to share screen. Click <span>Start Screen Share</span> to begin!`;
        let statusType = 'initialize';
        this.updateStatus(message, statusType);
    }

    static getCSRFToken() {
        return document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
    }
}