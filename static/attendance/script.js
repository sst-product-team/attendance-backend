// Function to fetch JSON data from a file
async function fetchJSONData() {
  try {
    const response = await fetch("/attendance/get_current_class_attendance/");
    const jsonData = await response.json();
    return jsonData;
  } catch (error) {
    console.error("Error fetching JSON data:", error);
    return [];
  }
}

async function isStaff() {
  try {
    const response = await fetch("/attendance/can_mark_attendance/");
    const jsonData = await response.json();
    return jsonData;
  } catch (error) {
    console.error("Error fetching JSON data:", error);
    return [];
  }
}

// Function to populate the table
async function populateTable() {
  var tableBody = document.getElementById("attendanceTableBody");
  var className = document.getElementById("Class");

  // Fetch JSON data
  const jsonData = await fetchJSONData();
  const canMarkAttendance = await isStaff();

  // Clear existing rows
  tableBody.innerHTML = "";
  className.innerHTML = `Attendance for ${jsonData["current_class"].name}`;

  // Loop through the JSON data and create table rows
  let allAttendance = jsonData["all_attendance"];
  for (let i = 0; i < allAttendance.length; i++) {
    var row = tableBody.insertRow();
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);

    cell1.innerHTML = i;
    cell2.innerHTML = allAttendance[i].name;
    cell3.innerHTML = allAttendance[i].mail;

    allAttendance[i].status = allAttendance[i].status.toLowerCase();

    if (canMarkAttendance) {
      cell4.innerHTML = `<select default=${allAttendance[i].status} id="${
        allAttendance[i].mail
      }">
      <option value="present" ${
        allAttendance[i].status === "present" ? "selected" : ""
      }>Present</option>
      <option value="absent" ${
        allAttendance[i].status === "absent" ? "selected" : ""
      }>Absent</option>
      <option value="proxy" ${
        allAttendance[i].status === "proxy" ? "selected" : ""
      }>Proxy</option>
      </select>`;

      // Add event listener to the dynamically created select element
      let selectElement = document.getElementById(`${allAttendance[i].mail}`);
      selectElement.addEventListener("change", function (event) {
        let selectedValue = event.target.value;
        let selectedMail = allAttendance[i].mail;
        console.log(selectedMail, selectedValue);
      });
    } else {
      cell4.innerHTML = allAttendance[i].status;
    }
  }
}

// Call the function to populate the table
populateTable();
