class Cell {

    constructor(cell, cellDetection, cellClass) {

        this.id = cell.id;
        this.region = cell.region;

    }

    static cellOrder() {
        const CELL_ORDER = [
            'blast', 'promyelocyte', 'myelocyte', 'metamyelocyte', 'neutrophil', 'monocyte', 'eosinophil', 
            'basophil', 'lymphocyte', 'plasma-cell', 'erythroid-precursor', 'skippocyte', 'unclassified'
        ]
        return CELL_ORDER;
    }

    static devToken() {
        const DEV_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM4OTYzNjA3LCJpYXQiOjE3Mzg4NzcyMDcsImp0aSI6IjhhM2QxNWJhNjhhYTQ3NDVhNjZhMTBhNmU4YmVjNWM2IiwidXNlcl9pZCI6MX0.dozpURDSg6OsfVeThc6-Dt86gCHfvtazRfmsyPkgV7E';
        return DEV_TOKEN;
    }

    static cellItemClickHandler(element) {

        let caseStatus = document.getElementById('caseStatus');
        if (!caseStatus) {
            $(element).on('click', function() {

                let cell_id = $(this).data('id');
    
                $('.cell-image').not(this).removeClass('clicked');
                $(this).toggleClass('clicked');
                $(this).attr('tabindex', 0).focus();
                $('.cell-image').off('keyup');
    
                $(this).on('keyup', function(event) {
                    console.log('keyup ', event);
                    Cell.labelEventListener(event, cell_id);
                });
            });
        }
    }

	static label_dict = {

		'Digit1': 'blasts_and_blast_equivalents', // BLAST
		'Digit2': 'promyelocytes', // PROMYELOCYTE
		'Digit3': 'myelocytes', // MYELOCYTE
		'Digit4': 'metamyelocytes', // METAMYELOCYTE
		'Digit5': 'neutrophils', // NEUTROPHIL/BAND

		'KeyA': 'monocytes', // MONOCYTE
		'KeyS': 'eosinophils', // EOSINOPHIL
		//'KeyD': 'basophil', // BASOPHIL
		
		'KeyF': 'lymphocytes', // LYMPHOCYTE
		'KeyJ': 'plasma_cells', // PLASMA CELL

		'KeyK': 'erythroid_precursors', // ERYTHROID PRECURSOR

		'KeyL': 'skippocytes' // OTHER
		
		// 'Period': 'L10', // LYMPHOCYTE
		// 'KeyH': 'HA10', // HAIRY CELL

	}

    static labelEventListener(event, cell_id) {

		var code = event.code;
        var new_label = this.label_dict[code]
        
        if (new_label != undefined) {
            return Cell.labelCurrentCell(new_label, cell_id);
        } else {
            console.log(new_label, 'ERROR');
        }

	}

    static getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break
                }
            }
        }
        return cookieValue;
    }

    static labelCurrentCell(label, cell_id) {

        let case_id = window.location.pathname.split('/')[2]
        let CELL_URL = `/api/cells/json_cell/${ case_id }/`;

		fetch(CELL_URL, {
            method: 'POST',
            headers: {
                'X-CSRFToken': Cell.getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            credentials: "include",
            body: JSON.stringify({
                cell_id: cell_id,
                cell_label: label
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Cell.updateCellDisplay(label);

                // UPDATE CELL PERCENT DISPLAY
                for (const[cellType, percentage] of Object.entries(data.diff_counts.percentages)) {
                    let diffElement = document.querySelector(`#${ cellType }_percent`);
                    if (diffElement) {
                        diffElement.innerHTML = `${ percentage }%`;
                    }
                }

                // UPDATE CELL COUNT DISPLAY
                for (const [cellType, count] of Object.entries(data.diff_counts.counts)) {
                    let countElement = document.querySelector(`#${ cellType }_count`);
                    if (countElement) {
                        countElement.innerHTML = `(${ count })`;
                    }
                }
            }
        })
    
	}

    static updateCellDisplay(new_label) {

		var old_cell = $('.clicked').first();
        var old_label = old_cell.data('class');

		if (old_label != new_label) {

            let old_section = document.querySelector(`#${ old_label }`);
            old_cell.remove();

            if (old_section && old_section.querySelector('.cell-images') && old_section.querySelector('.cell-images').children.length === 0) {
                old_section.remove();
            }

            let targetSection = document.querySelector(`#${ new_label }`);
            if (!targetSection) {
                targetSection = Cell.insertCellSection(new_label);
            }

            // ENSURE JQUERY OBJECT IS PURE DOM ELMENT
            targetSection.querySelector('.cell-images').prepend(old_cell[0]);

            old_cell.removeClass('clicked');
            old_cell.addClass('changed');
            old_cell.attr('data-class', new_label);
            old_cell.find('img').attr("alt", new_label);
            old_cell.off('click');

            Cell.cellItemClickHandler(old_cell[0]);

		}

	}

    static createCellSection(class_name) {

        const newSection = document.createElement('section');

        newSection.id = class_name;
        newSection.classList.add('cell-classification');
        newSection.dataset.class = class_name;
        let class_name_title = class_name.replace(/(?:^|-)(\w)/g, (_, char) => char.toUpperCase());
        newSection.innerHTML = `
            <h3>${ class_name_title }</h3>
            <div class="cell-images"></div>
        `;

        return newSection;
    }

    static insertCellSection(class_name) {

        const CELL_ORDER = Cell.cellOrder();
        
        const cellContainer = document.querySelector('.cell-classification-container');
        const existingSections = [...cellContainer.querySelectorAll('.cell-classification')];
        const newIndex = CELL_ORDER.indexOf(class_name);
        let insertedBeforeElement = null;

        for (let section of existingSections) {
            const sectionClass = section.dataset.class;
            const sectionIndex = CELL_ORDER.indexOf(sectionClass);

            if (sectionIndex > newIndex) {
                insertedBeforeElement = section;
                break;
            }
        }

        const newSection = Cell.createCellSection(class_name);

        if (insertedBeforeElement) {
            cellContainer.insertBefore(newSection, insertedBeforeElement)
        } else {
            cellContainer.appendChild(newSection);
        }

        return newSection;
    }

    static async fetchCellCounts(caseID) {

        caseID = '1';

        try {
            const response = await fetch(`/api/cells/cell_counts/${ caseID}`, {
                method: "GET",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${ Cell.devToken() }`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${ response.status }`);
            }

            const data = await response.json();

        } catch (error) {
            console.log('error fetching cell counts ', error);
        }

    } 

    static async getDiff(caseID) {

        caseID = '1';

        try {
            const response = await fetch(`/api/cells/get_diff/${ caseID }`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${ Cell.devToken() }`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${ response.status }`);
            }

            const data = await response.json();

        } catch (error) {
            console.log('Error fetching diff ', error);
        }
    }

}
