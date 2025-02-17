export class CropManager {
    constructor(screenShare, uiManager) {
        this.uiManager = uiManager;
        this.elements = uiManager.getElements();

        this.screenShare = screenShare;
        // this.uiManager = uiManager;
        this.isDrawing = false;
        this.startX = 0;
        this.startY = 0;
        this.currentX = 0;
        this.currentY = 0;
        
        this.cropBox = document.querySelector('.crop-box');
        this.cropOverlay = document.querySelector('.crop-overlay');
        this.previewCanvas = document.getElementById('previewCanvas');
        this.ctx = this.previewCanvas.getContext('2d');
        this.canDraw = false;
    }

    initialize() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.cropOverlay.addEventListener('mousedown', (e) => this.startDraw(e));
        this.cropOverlay.addEventListener('mousemove', (e) => this.draw(e));
        this.cropOverlay.addEventListener('mouseup', () => this.endDraw());
        // this.cropOverlay.addEventListener('mouseleave', () => this.endDraw());
    }

    enableDrawing() {
        this.canDraw = true;
    }

    disableDrawing() {
        this.canDraw = false;
    }

    startDraw(e) {
        if (!this.canDraw) return;

        const { resetCropButton } = this.elements;
        this.isDrawing = true;
        const bounds = this.cropOverlay.getBoundingClientRect();
        this.startX = e.clientX - bounds.left;
        this.startY = e.clientY - bounds.top;
        this.cropBox.style.display = 'block';
        // this.uiManager.showResetCropButton();
        // this.uiManager.resetCropButton.show();
        // resetCropButton.show();
        resetCropButton.style.display = 'block';
    }

    draw(e) {
        if (!this.canDraw || !this.isDrawing) return;
        
        const bounds = this.cropOverlay.getBoundingClientRect();
        this.currentX = Math.min(Math.max(e.clientX - bounds.left, 0), bounds.width);
        this.currentY = Math.min(Math.max(e.clientY - bounds.top, 0), bounds.height);

        const left = Math.min(this.startX, this.currentX);
        const top = Math.min(this.startY, this.currentY);
        const width = Math.abs(this.currentX - this.startX);
        const height = Math.abs(this.currentY - this.startY);

        this.cropBox.style.left = left + 'px';
        this.cropBox.style.top = top + 'px';
        this.cropBox.style.width = width + 'px';
        this.cropBox.style.height = height + 'px';

        const dimensions = this.NEWgetCropDimensions();
        this.uiManager.videoCropDimensions(dimensions)
        this.uiManager.updateDimensions(
            this.screenShare.getTrueWidth(),
            this.screenShare.getTrueHeight(),
            dimensions.width,
            dimensions.height,
            dimensions.scale
        );
    }

    endDraw() {
        this.isDrawing = false;

        // Only enable confirm button if there's a valid crop selection
        const cropBox = this.cropBox.getBoundingClientRect();
        if (cropBox.width > 10 && cropBox.height > 10) {  // Ensure minimum size
            this.uiManager.updateConfirmRecordButton(true);
            let message = `Select <span>Confirm Region</span> to begin recording.`;
            let statusType = 'active';
            this.uiManager.updateStatus(message, statusType);
        } else {
            this.cropBox.style.display = 'none';  // Hide tiny/invalid selections
            this.uiManager.updateConfirmRecordButton(false);
            this.uiManager.updateStatus("Please select a larger preview area");
        }
    }

    NEWgetCropDimensions() {
        const cropBox = this.cropBox.getBoundingClientRect();
        const sharedScreenBox = this.screenShare.elements.sharedScreen.getBoundingClientRect(); // ✅ Get video position
    
        const bounds = this.screenShare.getVideoBounds();
        const scale = this.screenShare.getTrueWidth() / bounds.width;
    
        // ✅ Adjust cropBox position relative to `sharedScreen`
        const adjustedLeft = cropBox.left - sharedScreenBox.left;
        const adjustedTop = cropBox.top - sharedScreenBox.top;
    
        const dimensions = {
            width: Math.round(cropBox.width * scale),
            height: Math.round(cropBox.height * scale),
            left: Math.round(adjustedLeft * scale),
            top: Math.round(adjustedTop * scale),
            scale: scale
        };
    
        return dimensions;    
    }

    getCropDimensions() {

        const position = this.cropBox.getBoundingClientRect();
        const bounds = this.screenShare.getVideoBounds();
        const scale = this.screenShare.getTrueWidth() / bounds.width;
        const width = Math.abs(this.currentX - this.startX);
        const height = Math.abs(this.currentY - this.startY);
        
        return {
            width: Math.round(width * scale),
            height: Math.round(height * scale),
            left: position.left,
            top: position.top,
            scale: scale
        };
    }

    resetCrop() {
        this.cropBox.style.display = 'none';
        this.ctx.clearRect(0, 0, this.previewCanvas.width, this.previewCanvas.height);
        this.uiManager.updateConfirmRecordButton(false);  // Disable confirm button on reset
        this.uiManager.updateStatus("Please select a preview area");
    }

    updatePreview() {
        if (!this.screenShare.isActive() || this.cropBox.style.display === 'none') {
            requestAnimationFrame(() => this.updatePreview());
            return;
        }
        
        try {
            const bounds = this.screenShare.getVideoBounds();
            const scale = this.screenShare.getTrueWidth() / bounds.width;

            const sharedScreenBox = this.screenShare.elements.sharedScreen.getBoundingClientRect();
            const cropBox = this.cropBox.getBoundingClientRect();
            
            // const left = Math.min(this.startX, this.currentX);
            // const top = Math.min(this.startY, this.currentY);
            // const width = Math.abs(this.currentX - this.startX);
            // const height = Math.abs(this.currentY - this.startY);

            const left = cropBox.left - sharedScreenBox.left;
            const top = cropBox.top - sharedScreenBox.top;
            const width = cropBox.width;
            const height = cropBox.height;
            
            const trueX = left * scale;
            const trueY = top * scale;
            const trueBoxWidth = width * scale;
            const trueBoxHeight = height * scale;
            
            this.previewCanvas.width = trueBoxWidth;
            this.previewCanvas.height = trueBoxHeight;
            
            this.ctx.drawImage(
                this.screenShare.getVideoElement(),
                trueX,
                trueY,
                trueBoxWidth,
                trueBoxHeight,
                0,
                0,
                this.previewCanvas.width,
                this.previewCanvas.height
            );

            if (this.uiManager.previewWindow) {
                const mirroredCtx = this.uiManager.previewWindow.document.getElementById('mirroredCanvas').getContext('2d');
                mirroredCtx.clearRect(0, 0, this.uiManager.previewWindow.document.getElementById('mirroredCanvas').width, this.uiManager.previewWindow.document.getElementById('mirroredCanvas').height);
                mirroredCtx.drawImage(this.previewCanvas, 0, 0)

            }
            
            requestAnimationFrame(() => this.updatePreview());
        } catch (error) {
            console.error('Error in updatePreview:', error);
            requestAnimationFrame(() => this.updatePreview());
        }
    }

    show() {
        this.cropOverlay.style.display = 'block';
    }

    hide() {
        this.cropOverlay.style.display = 'none';
        this.cropBox.style.display = 'none';
    }
}