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
        text: 'This is the summary sidebar where you can find cell types, counts and percents.',
        attachTo: { element: '.sidebar', on: 'right' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 3: Highlight an individual sidebar element/link
    tour.addStep({
        id: 'step3',
        text: 'Click on these links to navigate directly to a specific cell type.',
        attachTo: { element: '.sidebar .cell-link:first-child', on: 'right' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 4: Highlight 'keybinding' icons
    tour.addStep({
        id: 'step4',
        text: 'These icons represent key bindings used to re-label a selected cell.',
        attachTo: { element: document.querySelector('.keybinding'), on: 'right' },
        buttons: [{
            text: 'Next',
            action: tour.next
        }]
    })

    // Step 5: Highlight a single cell image
    tour.addStep({
        id: 'step5',
        text: 'These are the cell images. Click on them to activate re-labeling.',
        attachTo: { element: '.cell-image:first-of-type', on: 'top' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 6: Highlight "Close Case" button
    tour.addStep({
        id: 'step6',
        text: 'Click this button to mark the case as completed and prevent any further changes.',
        attachTo: { element: '#closeCase', on: 'top' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 7: Highlight case OUPUT buttons
    tour.addStep({
        id: 'step7',
        text: 'Use these buttons to save the diff report. You can copy the data to clipboard or save the entire HTML page.',
        attachTo: { element: '#copyDiff', on: 'top' },
        buttons: [{ text: 'Next', action: tour.next }]
    });

    // Step 8 Highlight "Help" link in navbar and end tour
    tour.addStep({
        id: 'step8',
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
