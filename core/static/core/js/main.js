import { ScreenShare } from './screenShare.js';
import { CropManager } from './cropManager.js';
import { UIManager } from './uiManager.js';
import { startTour } from './Tour.js';
import { uploadState } from './uploadState.js';

document.addEventListener('DOMContentLoaded', () => {

    const uiManager = new UIManager();
    const screenShare = new ScreenShare(uiManager);

    uiManager.setScreenShare(screenShare);

    const cropManager = new CropManager(screenShare, uiManager);

    uiManager.setCropManager(cropManager);

    // Initialize the application
    uiManager.initialize(screenShare, cropManager);
    screenShare.initialize();
    cropManager.initialize();

    // console.log("✅ UI components initialized.");  // ✅ Debugging log

    // // Start tour AFTER ensuring everything is loaded
    // setTimeout(() => {
    //     console.log("🚀 Calling startTour()...");
    //     startTour();
    // }, 1000);
});
