export class UIManager {
    constructor(screenShare) {
        // this.cropManager = cropManager;
        this.screenShare = screenShare;
        // DOM elements
        this.elements = {
            shareButton: document.getElementById('shareButton'),
            stopButton: document.getElementById('stopButton'),
            resetCropButton: document.getElementById('resetCrop'),

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
            hiddenScreenRecorder: document.getElementById('hiddenScreenRecorder'),

        };

        this.record = false;

    }

    initialize(screenShare, cropManager) {
        // Any initial UI setup
        console.log('crop ', cropManager);

        this.elements.recordButton.addEventListener("click", () => {
            console.log('click');
            this.showConfirmRecordButton();
        });

        // this.elements.confirmRecordButton.addEventListener("click", () => {
        //     this.startModalPreview(screenShare.stream);
        // });

        this.elements.stopRecordingButton.addEventListener("click", () => {
            screenShare.stopRecording();
            screenShare.stopSharing();
            // this.closePreviewModal();
        });

        // this.elements.confirmRecordButton.addEventListener("click", () => {
        //     this.startModalPreview();
        // });

        this.elements.confirmRecordButton.addEventListener("click", () => {
            console.log('confirmRecordButton ', cropManager);
            this.startModalPreview(cropManager, screenShare);
            // screenShare.startRecording(screenShare.stream);
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

        // this.startModalPreview(this.screenShare.stream);
    }

    startModalPreview(cropManager, screenShare) {

        console.log('startModalPreview stream ', screenShare.stream);
    
        if (!cropManager) {
            console.error("❌ Error: cropManager is undefined.");
            return;
        }
    
        const cropDimensions = cropManager.getCropDimensions();
    
        if (!cropDimensions.width || !cropDimensions.height) {
            alert("❌ Please select an area before recording.");
            return;
        }

        if (!screenShare || !screenShare.stream) {
            console.error("❌ Error: No active screen share stream!");
            alert("❌ No active screen share. Start screen sharing first.");
            return;
        }
    
        // ✅ Create new popup window
        let modalWindow = window.open("", "_blank", `width=${cropDimensions.width + 50},height=${cropDimensions.height + 100}`);
        
        // ✅ Write HTML content for the new window
        modalWindow.document.write(`
            <html>
            <head>
                <title>Live Preview</title>
                <style>
                    body {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        background-color: #222;
                        color: white;
                        font-family: Arial, sans-serif;
                        margin: 0;
                        height: 100vh;
                    }
                    video {
                        width: 100%;
                        height: auto;
                        border-radius: 8px;
                        box-shadow: 0px 4px 8px rgba(255, 255, 255, 0.2);
                    }
                    button {
                        margin-top: 10px;
                        padding: 10px 15px;
                        font-size: 16px;
                        background: red;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        transition: background 0.3s ease-in-out;
                    }
                    button:hover {
                        background: darkred;
                    }
                </style>
            </head>
            <body>
                <h3>Live Preview</h3>
                <video id="popupPreviewVideo" autoplay playsinline></video>
                <button id="stopRecordingButton">🛑 Stop Recording</button>
            </body>
            </html>
        `);

        // ✅ Wait for modal to fully load before assigning the stream
        modalWindow.onload = () => {
            console.log("✅ Modal loaded, sending stream...");
            modalWindow.postMessage({ action: "setStream", stream: screenShare.stream }, "*");
        };
        // const checkModalLoaded = setInterval(() => {
        //     if (modalWindow.document && modalWindow.document.readyState === "complete") {
        //         console.log("✅ Modal loaded, sending stream...");
        //         modalWindow.postMessage({ action: "setStream", stream: screenShare.stream }, "*");
        //         clearInterval(checkModalLoaded);
        //     }
        // }, 500);

        // ✅ Handle stop recording event from the modal
        window.addEventListener("message", (event) => {
            if (event.data.action === "stopRecording") {
                console.log("🛑 Stop button clicked in popup!");
                screenShare.stopRecording();
                modalWindow.close();
            }
        });
        
        // // ✅ Assign the existing screen share stream to the new window's video
        // const popupPreviewVideo = modalWindow.document.getElementById("popupPreviewVideo");
        // popupPreviewVideo.srcObject = this.elements.sharedScreen.srcObject;
    
        // // ✅ Handle stop button inside popup
        // modalWindow.document.getElementById("stopRecordingButton").addEventListener("click", () => {
        //     console.log("🛑 Stop button clicked in popup!");
        //     this.screenShare.stopRecording();
        //     modalWindow.close();
        // });
    
        console.log("🎥 Live Preview is now open in a new window.");
    }
    

    // startModalPreview(cropManager) {
    //     console.log("🚀 Opening Modal in a New Window...");
    
    //     if (!cropManager) {
    //         console.error("❌ Error: cropManager is undefined.");
    //         return;
    //     }
    
    //     const cropDimensions = cropManager.getCropDimensions();
    //     console.log("📏 Corrected Crop Dimensions:", cropDimensions);
    
    //     if (!cropDimensions.width || !cropDimensions.height) {
    //         alert("❌ Please select an area before recording.");
    //         return;
    //     }
    
    //     // ✅ Open the modal in a new window
    //     let modalWindow = window.open("/preview_modal/", "_blank", `width=${cropDimensions.width + 50},height=${cropDimensions.height + 100}`);
    
    //     // ✅ Ensure the stream is available before sending to the modal
    //     // const waitForStream = setInterval(() => {
    //     //     if (this.elements.previewVideo.srcObject) {
    //     //         console.log("✅ Stream available, sending to modal.");
    //     //         modalWindow.postMessage({ streamId: this.elements.previewVideo.srcObject.id }, "*");
    //     //         clearInterval(waitForStream);
    //     //     }
    //     // }, 500); // Check every 500ms

    //     modalWindow.onload = () => {
    //         console.log("✅ Modal loaded, sending stream...");
    //         modalWindow.postMessage({ action: "setStream", stream: this.screenShare.stream.id }, "*");
    //     };    
    
    //     // ✅ Handle stop recording event
    //     window.addEventListener("message", (event) => {
    //         if (event.data.action === "stopRecording") {
    //             console.log("🛑 Stop button clicked in popup!");
    //             this.screenShare.stopRecording();
    //             modalWindow.close();
    //         }
    //     });
    
    //     console.log("🎥 Live Preview is now open in a new window.");
    // }
    

    // startModalPreview(cropManager, screenShare) {

    //     const cropDimensions = cropManager.NEWgetCropDimensions();
    
    //     const cropBox = this.elements.cropBox.getBoundingClientRect();
    //     const sharedScreenBox = this.elements.sharedScreen.getBoundingClientRect();

    //     if (!cropDimensions.width || !cropDimensions.height) {
    //         alert("Please select an area before recording.");
    //         return;
    //     }

    //     // this.elements.previewModal.style.display = "flex";
    //     let modalWindow = window.open("/preview_modal", "_blank", `width=${cropDimensions.width + 50},height=${cropDimensions.height + 100}`);

    //     modalWindow.onload = () => {
    //         modalWindow.postMessage({ streamId: this.elements.previewVideo.srcObject.id }, "*");
    //     };

    //     window.addEventListener("message", (event) => {
    //         if (event.data.action === "stopRecording") {
    //             console.log("🛑 Stop button clicked in popup!");
    //             this.screenShare.stopRecording();
    //             modalWindow.close();
    //         }
    //     });


        // this.elements.cropOverlay.style.display = "block";``
        // this.elements.cropOverlay.style.border = "2px dashed red";

        // const modal = this.elements.previewModal;
        // const modalContent = modal.querySelector(".modal-content");
        // const previewVideo = this.elements.previewVideo;
        // // modalContent.style.width = `${ cropBox.width }px`;
        // // modalContent.style.height = `${ cropBox.height }px`;
        // modalContent.style.width = `${ cropDimensions.width }px`;
        // modalContent.style.height = `${ cropDimensions.height }px`;

        // previewVideo.style.width = `${ cropDimensions.width }px`;
        // previewVideo.style.height = `${ cropDimensions.height }px`;


        // console.log('assign screen stream ', screenShare.stream);

        // this.updateModalPreviewPosition(cropManager);

        // // ✅ Debug: Remove old listeners before adding new ones
        // window.removeEventListener("scroll", this.updateModalPreviewPosition);
        // window.removeEventListener("resize", this.updateModalPreviewPosition);

        // // ✅ Add event listeners for live updates
        // window.addEventListener("scroll", () => {
        //     console.log("🔄 Scrolling detected!");
        //     this.updateModalPreviewPosition(cropManager);
        // });

        // window.addEventListener("resize", () => {
        //     console.log("🔄 Resizing detected!");
        //     this.updateModalPreviewPosition(cropManager);
        // });

        // this.elements.previewVideo.srcObject = screenShare.stream;
        // this.elements.hiddenScreenRecorder.srcObject = screenShare.stream;
        // ✅ Adjust for `sharedScreen` position
        // this.elements.previewVideo.style.width = `${this.elements.sharedScreen.videoWidth}px`;
        // this.elements.previewVideo.style.height = `${this.elements.sharedScreen.videoHeight}px`;
        // this.elements.previewVideo.style.objectFit = "cover";
        // this.elements.previewVideo.style.position = "absolute";
        // this.elements.previewVideo.style.left = `-${cropDimensions.left}px`;
        // this.elements.previewVideo.style.top = `-${cropDimensions.top}px`;

        // console.log("🎥 previewVideo.srcObject:", this.elements.previewVideo.srcObject);
        // console.log("🎥 hiddenScreenRecorder.srcObject:", this.elements.hiddenScreenRecorder.srcObject);    

        // this.elements.previewVideo.style.width = `${ this.elements.sharedScreen.videoWidth }px`;
        // this.elements.previewVideo.style.height = `${ this.elements.sharedScreen.videoHeight }px`;
        // this.elements.previewVideo.style.objectFit = "cover";
        // this.elements.previewVideo.style.position = "absolute";
        // this.elements.previewVideo.style.left = `${ cropBox.left }px`;
        // this.elements.previewVideo.style.top = `${ cropBox.top }px`;

        // this.elements.previewVideo.style.clipPath = `inset(${cropBox.top}px ${this.elements.sharedScreen.videoWidth - cropBox.right}px ${this.elements.sharedScreen.videoHeight - cropBox.bottom}px ${cropBox.left}px)`;
        // this.elements.previewVideo.style.clipPath = `inset(${cropBox.top}px ${this.elements.sharedScreen.videoWidth - cropBox.right}px ${this.elements.sharedScreen.videoHeight - cropBox.bottom}px ${cropBox.left}px)`;

        // console.log("🖼️ Clip Path Applied:", this.elements.previewVideo.style.clipPath);

    // }

    // startModalPreview() {
    //     const cropBox = this.elements.cropBox.getBoundingClientRect();
    // }

    updateModalPreviewPosition(cropManager) {
        if (!cropManager) {
            console.error("❌ updateModalPreviewPosition: cropManager is undefined.");
            return;
        }
    
        const cropDimensions = cropManager.NEWgetCropDimensions();
        console.log("🔄 Updating Modal Position:", cropDimensions);
    
        if (!cropDimensions.width || !cropDimensions.height) {
            console.error("❌ Invalid crop dimensions.");
            return;
        }
    
        // ✅ Recalculate position relative to `sharedScreen`
        const sharedScreenBox = this.elements.sharedScreen.getBoundingClientRect();
    
        this.elements.previewVideo.style.width = `${this.elements.sharedScreen.videoWidth}px`;
        this.elements.previewVideo.style.height = `${this.elements.sharedScreen.videoHeight}px`;
        this.elements.previewVideo.style.objectFit = "cover";
        this.elements.previewVideo.style.position = "absolute";
        this.elements.previewVideo.style.left = `-${cropDimensions.left}px`;
        this.elements.previewVideo.style.top = `-${cropDimensions.top}px`;
    }
    

    closePreviewModal() {
        this.elements.previewModal.style.display = "none";
        this.elements.previewVideo.srcObject = null;
        // this.elements.cropOverlay.style.display = "none";
    }

    lockToPreviewArea() {
        this.elements.cropOverlay.style.border = "3px solid red";
        this.updateStatus('Recroding started. Viewing limitted to viewing area.');
    }

    toggleRecordButton() {
        // this.elements.recordButton.innerHTML = `
        //     <svg class="icon" viewBox="0 0 24 24">
        //         <rect x="6" y="6" width="12" height="12"/>
        //     </svg>
        //     Stop Recording
        // `;
        this.elements.confirmRecordButton.style.display = "none";
        this.recording = true;
    }

    resetDisplay() {
        this.elements.cropOverlay.style.border = "none";
        this.elements.confirmRecordButton.style.display = "none";
        // this.elements.recordButton.innerHTML = `
        //     <svg class="icon" viewBox="0 0 24 24">
        //         <circle cx="12" cy="12" r="8"/>
        //     </svg>
        //     Start Recording
        // `;
        this.recording = false;
        this.updateStatus('Recording stopped');
    }

    updateStatus(message) {
        console.log(message);
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