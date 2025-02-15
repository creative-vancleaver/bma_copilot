class Case {
    
    constructor(c) {
        this.case_id = c.case_id;
        this.case_status = c.case_status;
    }

    static updateCaseStatus(caseId, newStatus) {
        fetch(`/api/cases/${ caseId }/update-status/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': Case.getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `status=${ encodeURIComponent(newStatus)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Status updated to: ${ data.new_status }`);
                $('#closeCase').text('Case Closed');
            } else {
                alert(`Error: ${ data.error }`);
            }
        })
        .catch(error => console.log('Error: ', error));
    }

    static getCSRFToken() {
        return document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
    }

}