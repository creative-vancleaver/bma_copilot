import { ScreenShare } from "./screenShare.js";

// Global state for tracking upload progress
export const uploadState = {
    progress: 0,
    status: 'idle',
    error: null
};

// Global state for tracking processing progress
export const processingState = {
    progress: 0,
    status: 'idle',
    message: '',
    error: null
};

// UI update function
export function updateProgressBar() {

    const statusDiv = document.getElementById('status');
    const recordingIndicator = document.getElementById('recordingIndicator');
    const progressBar = document.getElementById('progressBar') || createProgressBar();
    
    if (uploadState.status === 'uploading') {

        // progressBar.style.width = `${ uploadState.progress }`;
        // progressBar.classList.add('uploading');
        statusDiv.textContent = `Uploading: ${uploadState.progress}%`;
        recordingIndicator.classList.add('uploading');

    } else if (processingState.status === 'pending') {

        // progressBar.style.width = `${ processingState.progress }`;
        // progressBar.classList.remove('uploading');
        // progressBar.classList.add('processing');
        statusDiv.innerHTML = `Your video is being analyzed. Keep your eye here for updates.`
        recordingIndicator.classList.remove('uploading', 'success');
        recordingIndicator.classList.add('processing');

    } else if (processingState.status === 'processing') {

        statusDiv.textContent = `${processingState.message} (${processingState.progress}%)`;
        recordingIndicator.classList.remove('uploading');
        recordingIndicator.classList.add('processing');

    } else if (processingState.status === 'completed') {

        statusDiv.textContent = 'Analysis complete!';
        recordingIndicator.classList.remove('uploading', 'processing', 'pending');
        recordingIndicator.classList.add('success');

    } else if (uploadState.status === 'completed') {

        progressBar.style.width = `${ uploadState.progress }`;
        statusDiv.textContent = 'Upload complete!';
        recordingIndicator.classList.remove('uploading');
        recordingIndicator.classList.add('success');

    } else if (uploadState.status === 'error' || processingState.status === 'error') {

        const error = uploadState.error || processingState.error;
        statusDiv.textContent = `Error: ${error}`;
        recordingIndicator.classList.remove('uploading', 'processing', 'pending');
        recordingIndicator.classList.add('error');

    }
}

function createProgressBar() {
    const progressContainer = document.getElementById('dimensions');
    const progressBar = document.createElement('div');
    progressBar.id = 'progressBar';
    progressBar.style.width = '0%';
    progressBar.style.height = '100%';
    progressBar.style.transition = 'width 0.3s ease-in-out';

    progressContainer.replaceChildren(progressBar);
    
    return progressBar;
}

export function checkVideoStatus(videoId) {

    const MAX_CHECK_TIME = 300000 // 5 MINUTES
    const CHECK_INTERVAL = 3000; // 3 SECONDS
    let elapsedTime = 0;

    async function fetchStatus() {
        try {

            elapsedTime += CHECK_INTERVAL;

            if (elapsedTime >= MAX_CHECK_TIME) {
                clearInterval(statusCheckInterval);
                processingState.status = 'error';
                processingState.error = 'Processing timeout - Please check back later.';
                processingState.message = 'Processing timeout';
                updateProgressBar()
                return;
            }

            const getResponse = await fetch(`/api/cases/video-status/${ videoId }`);
            const getResponseData = await getResponse.json();
            console.log('getResponse ', getResponseData)

            // PARSE NESTED JSON STRING
            const data = JSON.parse(getResponseData.body);
            console.log('data ========= ', data);

            if (getResponse.ok) {
                processingState.status = data.status;
                processingState.message = data.message || 'Processing...';
                processingState.progress = data.progress || 25;
                console.log('Updated Processing State:', processingState);


                if (data.status === 'completed') {
                    processingState.status = 'completed';
                    clearInterval(statusCheckInterval);

                    const putResponse = await fetch('/api/cases/video-status/', {
                        method:'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': ScreenShare.getCSRFToken()
                        },
                        body: JSON.stringify({ video_id: videoId })
                    });
                    console.log("putResponse ", putResponse);
                    
                } else if (data.status === 'error') {
                    processingState.status = 'error';
                    processingState.error = data.error || 'Processing failed.';
                    clearInterval(statusCheckInterval);
                }

                updateProgressBar();

            } else {
                console.log('Error fetching video status: ', data);
            }
        } catch (error) {
            console.log('Network error: ', error);
        }
    }

    // CHECK STATUS EVERY 3 SECONDS
    const statusCheckInterval = setInterval(fetchStatus, 3000);

    fetchStatus();
}