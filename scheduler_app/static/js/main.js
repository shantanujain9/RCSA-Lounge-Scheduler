document.addEventListener('DOMContentLoaded', (event) => {
    let tableClickListenerSet = false;


function getCookie(name) {
    let value = "; " + document.cookie;
    let parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
}


let excludedSlots = new Set();  // Maintain a list of excluded slots

function setUpTableClickListener() {
    if (tableClickListenerSet) return;
    document.getElementById('availabilityDisplay').addEventListener('click', function(event) {
        let target = event.target;
        
        if (target.tagName.toLowerCase() === 'td') {
            let row = target.parentNode.rowIndex-1;
            let col = target.cellIndex-1;
            let slotIdentifier = `${row}-${col}`;
            

            if (excludedSlots.has(slotIdentifier)) {
                // Remove from set if it's already there
                excludedSlots.delete(slotIdentifier);
                target.classList.remove('excluded');
            } else {
                // Otherwise, add it to the set and update its appearance
                excludedSlots.add(slotIdentifier);
                target.classList.add('excluded');
            }
            
            event.stopPropagation();  // stop event propagation to ensure the click is captured
        }
    });
    tableClickListenerSet = true;
}

document.getElementById('uploadFilesButton').addEventListener('click', function(event) {
    event.preventDefault();
    //console.log("Upload button clicked");
    const fileInput = document.getElementById('fileUpload');
    const formData = new FormData();
    
    //console.log(fileInput.files.length);
    // Append all selected files to the FormData object
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append('files', fileInput.files[i]);
    }
    
    const csrfToken = getCookie('csrftoken');

    // Use the fetch API to send the formData to your server
    fetch('/upload_files/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken  // Make sure you send the CSRF token for POST requests
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('availabilityDisplay').innerHTML = data.availability_html;
    
        setUpTableClickListener();
        excludedSlots.clear();

    });
    //console.log("Preparing to send files to server");
});


// Modify the "generateSchedule" click handler to send the excluded slots to the server
document.getElementById("generateSchedule").addEventListener("click", function() {
    let excludedArray = Array.from(excludedSlots);  // Convert Set to Array

    // Create a FormData object to send files along with excluded slots
    const formData = new FormData();

    // Get file input reference and append files to formData
    const fileInput = document.getElementById('fileUpload');
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append('files', fileInput.files[i]);
    }

    // Append the excluded slots to the FormData object as a string
    formData.append('excluded_slots', JSON.stringify(excludedArray));

    fetch("/generate_schedule/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken  // Only send the CSRF token for POST requests
        },
        body: formData  // Send formData as the body
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        // Directly insert the received HTML table string into the desired container
        document.getElementById('finalizedDisplay').innerHTML = data.finalized_html;
        

        // Check if leftovers data exists and display it
        if (data.leftovers && Object.keys(data.leftovers).length > 0) {
            displayLeftovers(data.leftovers);
        }
    });
});

function displayLeftovers(leftovers) {
    let leftoversContainer = document.getElementById("leftoversDisplay");
    leftoversContainer.innerHTML = "<h4> Leftovers: </h4><ul>";

    for (let name in leftovers) {
        let hoursLeft = leftovers[name];
        let listItem = `<li>${name} - ${hoursLeft} hour(s) left</li>`;
        leftoversContainer.innerHTML += listItem;
    }

    leftoversContainer.innerHTML += "</ul>";
}


function displayData(data, tableId) {
    let table = document.getElementById(tableId);
    table.innerHTML = "";  // Clear existing rows

    for (let row of data) {
        let tr = document.createElement("tr");
        for (let cell of row) {
            let td = document.createElement("td");
            td.textContent = cell;
            tr.appendChild(td);
        }
        table.appendChild(tr);
    }
}
});