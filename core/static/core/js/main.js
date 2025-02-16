import { ScreenShare } from './screenShare.js';
import { CropManager } from './cropManager.js';
import { UIManager } from './uiManager.js';
import { startTour } from './Tour.js';
import { uploadState } from './uploadState.js';

document.addEventListener('DOMContentLoaded', () => {

    const uiManager = new UIManager();
    const screenShare = new ScreenShare(uiManager);
    const cropManager = new CropManager(screenShare, uiManager);

    // Initialize the application
    uiManager.initialize(screenShare, cropManager);
    screenShare.initialize();
    cropManager.initialize(screenShare);

    uiManager.setCropManager(cropManager);

    // console.log("✅ UI components initialized.");  // ✅ Debugging log

    // // Start tour AFTER ensuring everything is loaded
    // setTimeout(() => {
    //     console.log("🚀 Calling startTour()...");
    //     startTour();
    // }, 1000);
});
