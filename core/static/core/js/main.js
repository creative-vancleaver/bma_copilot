import { ScreenShare } from './screenShare.js';
import { CropManager } from './cropManager.js';
import { UIManager } from './uiManager.js';

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


});
