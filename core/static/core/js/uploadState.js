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
    error: null,
    caseId: null,
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

    } else if (processingState.status === 'pending' || processingState.status === 'running') {

        statusDiv.innerHTML = `${ processingState.message }`;
        recordingIndicator.classList.remove('uploading', 'success');
        recordingIndicator.classList.add('processing');

    } else if (processingState.status === 'processing') {

        statusDiv.textContent = `${processingState.message} (${processingState.progress}%)`;
        recordingIndicator.classList.remove('uploading');
        recordingIndicator.classList.add('processing');

    } else if (processingState.status === 'completed') {

        // statusDiv.textContent = 'Analysis complete!';
        statusDiv.textContent = `${ processingState.message }`;
        recordingIndicator.classList.remove('uploading', 'processing', 'pending');
        recordingIndicator.classList.add('success');

        // REDIRECT AFTER PROCESSING COMPLETE
        setTimeout(() => {
            window.location.href = `/case/${ processingState.caseId }`;
        }, 1500);

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

    const processingContainer = document.getElementById('processingContainer');
    const MAX_CHECK_TIME = 150000 // 2 MINUTES
    const CHECK_INTERVAL = 3000; // 3 SECONDS
    const MESSAGE_INTERVAL = 10000 // 15 SECONDS
    let elapsedTime = 0;

    const extractCaseId = (str) => {
        let [first, second] = str.split('_');
        return second ? `${ first }_${ second }` : first;
    }

    const caseId = extractCaseId(videoId);

    const progressMessages = [
        {
            time: MESSAGE_INTERVAL * 0,
            message: 'Initializing video analysis...',
            progress: 15
        },
        {
            time: MESSAGE_INTERVAL * 1,
            message: 'Processing microscope feed...',
            progress: 35
        },
        {
            time: MESSAGE_INTERVAL * 2,
            message: 'Detecting cell boundaries...',
            progress: 55
        },
        {
            time: MESSAGE_INTERVAL * 3,
            message: 'Analyzing cell morphology...',
            progress: 75
        },
        {
            time: MESSAGE_INTERVAL * 4,
            message: 'Finalizing results...',
            progress: 90
        }
    ];

    async function fetchStatus() {
        try {

            elapsedTime += CHECK_INTERVAL;

            if (elapsedTime >= MAX_CHECK_TIME) {
                clearInterval(statusCheckInterval);
                processingState.status = 'error';
                processingState.error = 'Processing timeout - Please check back later.';
                processingState.message = 'Processing timeout';
                processingContainer.style.display = 'none';
                updateProgressBar()
                return;
            }

            // UPDATE SIMULATED PROGRESS MESSAGE BASED ON ELAPSED TIME
            const currentMessage = progressMessages.reduce((acc, msg) => {
                if (elapsedTime >= msg.time) {
                    return msg;
                }
                return acc;
            }, progressMessages[0]);

            const getResponse = await fetch(`/api/cases/video-status/${ videoId }/`);
            const getResponseData = await getResponse.json();

            // PARSE NESTED JSON STRING
            const data = JSON.parse(getResponseData.body);
            console.log('GET response data = ', data)

            if (getResponse.ok) {
                processingState.caseId = caseId;
                processingState.status = data.status;


                // OVERRIDE WITH SIMULATED MESSAGES
                if (data.status === 'pending' || data.status === 'running') {
                    console.log('pending ', currentMessage.message);
                    processingState.message = currentMessage.message;
                    processingState.progress = currentMessage.progress;
                } else {
                    processingState.message = data.message || 'Processing...';
                    processingState.progress = data.progress || 25;
                }
                console.log('Updated Processing State:', processingState);

                if (data.status === 'completed') {
                    // processingState.status = 'completed';
                    // processingContainer.style.display = 'none';
                    // clearInterval(statusCheckInterval);


                    const getCellsJson = await fetch(`/api/cells/get_cells_file/${ caseId }/`);
                    const getCellsJsonResponse = await getCellsJson.json();
                    console.log('getCellsJSON = ', getCellsJsonResponse);

                    if (getCellsJson.ok) {
                        processingState.status = 'completed';
                        processingContainer.style.display = 'none';
                        clearInterval(statusCheckInterval);
                    } else {
                        console.log('ERROR ', getCellsJsonResponse);
                    }
                    // const putResponse = await fetch('/api/cases/video-status/', {
                    //     method:'PUT',
                    //     headers: {
                    //         'Content-Type': 'application/json',
                    //         'X-CSRFToken': ScreenShare.getCSRFToken()
                    //     },
                    //     body: JSON.stringify({ 
                    //         video_id: videoId,
                    //         case_id: caseId
                    //     })
                    // });
                    // console.log('putResponse ', putResponse);

                    // if (putResponse.ok) {
                    //     processingState.status = 'completed';
                    //     processingContainer.style.display = 'none';
                    //     clearInterval(statusCheckInterval);
                    // } else {
                    //     console.log('Error updating video status and fetching cell data ', getResponse.json());
                    //     processingContainer.style.display = 'none';
                    // }


                    
                } else if (data.status === 'error') {
                    processingState.status = 'error';
                    processingState.error = data.error || 'Processing failed.';
                    processingContainer.style.display = 'none';
                    clearInterval(statusCheckInterval);
                }

                updateProgressBar();

            } else {
                console.log('Error fetching video status: ', data);
                processingContainer.style.display = 'none';
            }
        } catch (error) {
            processingContainer.style.display = 'none';
            console.log('Network error: ', error);
        }
    }

    // CHECK STATUS EVERY 3 SECONDS
    const statusCheckInterval = setInterval(fetchStatus, 3000);

    fetchStatus();
}