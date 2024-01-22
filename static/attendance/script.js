let pendingRequests = 0;

// Function to fetch JSON data from a file
async function fetchJSONData() {
  try {
    const response = await fetch(getAttendanceURL);
    const jsonData = await response.json();
    return jsonData;
  } catch (error) {
    console.error("Error fetching JSON data:", error);
    return [];
  }
}

async function markAttendance(mail, status) {
  try {
    pendingRequests++;
    const response = await fetch(markAttendanceURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        mail,
        status,
      }),
    });
    const jsonData = await response.json();
    console.log(
      `Attendance of ${jsonData["mail"]} marked to ${jsonData["status"]}`
    );
    return jsonData;
  } catch (error) {
    console.error("Error fetching JSON data:", error);
    return [];
  } finally {
    pendingRequests--;
  }
}

// Function to check if there are pending requests
function hasPendingRequests() {
  return pendingRequests > 0;
}

// Warn the user if they try to leave the page with pending requests
window.addEventListener('beforeunload', function (e) {
  if (hasPendingRequests()) {
    const confirmationMessage = 'You have pending changes. Are you sure you want to leave?';
    e.returnValue = confirmationMessage; // Standard for most browsers
    return confirmationMessage; // For some older browsers
  }
});


// Function to populate the table
async function populateTable() {
  var tableBody = document.getElementById("attendanceTableBody");
  var className = document.getElementById("Class");

  // Fetch JSON data
  const jsonData = await fetchJSONData();
  const canMarkAttendance = await jsonData["can_mark_attendance"];

  console.log(jsonData);

  // Clear existing rows
  tableBody.innerHTML = "";
  className.innerHTML = `Attendance for ${jsonData["current_class"].name}`;

  // Loop through the JSON data and create table rows
  let allAttendance = jsonData["all_attendance"];
  allAttendance.sort((a, b) => (a.mail > b.mail ? 1 : -1));

  for (let i = 0; i < allAttendance.length; i++) {
    let row = tableBody.insertRow();
    let cell1 = row.insertCell(0);
    let cell2 = row.insertCell(1);
    let cell3 = row.insertCell(2);
    let cell4 = row.insertCell(3);

    cell1.innerHTML = i+1;
    cell2.innerHTML = allAttendance[i].name;
    cell3.innerHTML = allAttendance[i].mail;

    let getInnerHtmlForCellFour = (status, mail) => {
      status = status.toLowerCase();
      return `<select default=${status} id="${mail}">
            <option value="present" ${
              status === "present" ? "selected" : ""
            }>Present</option>
            <option value="absent" ${
              status === "absent" ? "selected" : ""
            }>Absent</option>
            <option value="proxy" ${
              status === "proxy" ? "selected" : ""
            }>Proxy</option>
            </select>`;
    };

    if (canMarkAttendance) {
      cell4.innerHTML = getInnerHtmlForCellFour(
        allAttendance[i].status,
        allAttendance[i].mail
      );

      // Add event listener to the dynamically created select element
      let selectElement = document.getElementById(`${allAttendance[i].mail}`);
      selectElement.addEventListener("change", async function (event) {
        let selectedValue = event.target.value;
        let selectedMail = allAttendance[i].mail;

        let response = await markAttendance(
          selectedMail,
          selectedValue.toLowerCase()
        );

        // Set the selected option to response.status
        let selectedIndex;
        switch (response.status.toLowerCase()) {
          case "present":
            selectedIndex = 0;
            break;
          case "absent":
            selectedIndex = 1;
            break;
          case "proxy":
            selectedIndex = 2;
            break;
          default:
            selectedIndex = 1; // Default to "present" if the status is not recognized
        }

        selectElement.selectedIndex = selectedIndex;

        cell3.innerHTML = response.mail;

        allAttendance[i].mail = response.mail;
        allAttendance[i].status = response.status;
      });
    } else {
      cell4.innerHTML = allAttendance[i].status;
    }
  }
}

// Call the function to populate the table
populateTable();

// Function to export table data to CSV
function exportToCSV() {
  const table = document.querySelector("#attendanceTable"); // Adjust this selector as needed
  const rows = table.querySelectorAll("tbody tr");

  // Prepare CSV content
  let csvContent = "data:text/csv;charset=utf-8,";
  csvContent += "Number,Name,Email,Attendance\n";

  rows.forEach((row) => {
    const cells = row.querySelectorAll("td");
    
    csvContent += `${cells[0].innerText},${cells[1].innerText},${cells[2].innerText},`;
    
    let select = cells[3].querySelector('select');
    let attendance_status;
    
    if(select){
      attendance_status = select.value;
    } else {
      attendance_status = cells[3].innerText;
    }
    csvContent += `${attendance_status}\n`;
  });

  // Create a data URI and initiate the download
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "attendance.csv");
  document.body.appendChild(link);
  link.click();
}

