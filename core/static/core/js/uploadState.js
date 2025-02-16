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
    
    if (uploadState.status === 'uploading') {

        statusDiv.textContent = `Uploading: ${uploadState.progress}%`;
        recordingIndicator.classList.add('uploading');

    } else if (processingState.status === 'processing') {

        statusDiv.textContent = `${processingState.message} (${processingState.progress}%)`;
        recordingIndicator.classList.remove('uploading');
        recordingIndicator.classList.add('processing');

    } else if (processingState.status === 'completed') {

        statusDiv.textContent = 'Analysis complete!';
        recordingIndicator.classList.remove('uploading', 'processing');
        recordingIndicator.classList.add('success');

    } else if (uploadState.status === 'completed') {

        statusDiv.textContent = 'Upload complete. Starting analysis...';
        recordingIndicator.classList.remove('uploading');

    } else if (uploadState.status === 'error' || processingState.status === 'error') {

        const error = uploadState.error || processingState.error;
        statusDiv.textContent = `Error: ${error}`;
        recordingIndicator.classList.remove('uploading', 'processing');
        recordingIndicator.classList.add('error');

    }
}

export function checkVideoStatus(videoId) {
    async function fetchStatus() {
        try{

            const response = await fetch(`/api/cases/video-status/${ videoId }`);
            const data = await response.json();

            if (response.ok) {
                processingState.status = data.status;
                processingState.message = data.message || 'Processing...';
                processingState.progress = data.progress || 0;

                if (data.status === 'completed') {
                    processingState.status = 'completed';
                    clearInterval(statusCheckInterval);
                } else if (data.status === 'error') {
                    processingState.status === 'error';
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