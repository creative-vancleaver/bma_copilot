import Shepherd from 'https://cdn.jsdelivr.net/npm/shepherd.js@10.0.0/+esm';

export function startTour() {
    console.log('start tour');
    const tour = new Shepherd.Tour({
        defaultStepOptions: {
            classes: 'shadow-md bg-purple-dark',
            // scrollTo: true,
            // showCancelLink: true
        }
    });

    // Step 1: Highlight entire classification container
    tour.addStep({
        id: 'step1',
        text: 'This section shows all classified cells.',
        attachTo: { element: '.cell-classification-container', on: 'top' },
        buttons: [{ 
            text: 'Next', 
            action: () => tour.next() }]
    });

    // Step 2: Highlight the entire sidebar
    tour.addStep({
        id: 'step2',
        text: 'This is the summary sidebar where you can find important case details.',
        attachTo: { element: '.sidebar', on: 'right' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 3: Highlight an individual sidebar element/link
    tour.addStep({
        id: 'step3',
        text: 'Click on these links to navigate to different cell types.',
        attachTo: { element: '.sidebar .cell-link:first-child', on: 'right' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 4: Highlight "Close Case" button
    tour.addStep({
        id: 'step4',
        text: 'Click this button to mark the case as completed.',
        attachTo: { element: '#closeCase', on: 'top' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 5: Highlight a single cell image
    tour.addStep({
        id: 'step5',
        text: 'These are the cell images. Click on them to interact.',
        attachTo: { element: '.cell-image:first-of-type', on: 'top' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 6: Highlight "Help" link in navbar and end tour
    tour.addStep({
        id: 'step6',
        text: 'Click this to restart the tour anytime.',
        attachTo: { element: '#help', on: 'bottom' },
        buttons: [{
            text: 'Finish',
            action: () => {
                localStorage.setItem('tourCompleted', 'true');
                tour.complete();
            }
        }]
    });

    tour.start();

}
