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