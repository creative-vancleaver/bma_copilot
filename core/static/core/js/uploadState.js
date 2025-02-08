// Global state for tracking upload progress
export const uploadState = {
    progress: 0,
    status: 'idle',
    error: null
};

// UI update function
export function updateProgressBar() {
    const statusDiv = document.getElementById('status');
    const recordingIndicator = document.getElementById('recordingIndicator');
    
    if (uploadState.status === 'uploading') {
        statusDiv.textContent = `Uploading: ${uploadState.progress}%`;
        recordingIndicator.classList.add('uploading');
    } else if (uploadState.status === 'completed') {
        statusDiv.textContent = 'Upload completed!';
        recordingIndicator.classList.remove('uploading');
        recordingIndicator.classList.add('success');
    } else if (uploadState.status === 'error') {
        statusDiv.textContent = `Error: ${uploadState.error}`;
        recordingIndicator.classList.remove('uploading');
        recordingIndicator.classList.add('error');
    }
}