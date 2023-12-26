Suggested design for backend API:

### 1. Mark Attendance:

#### Mark by Geo Location

- **Endpoint:** `POST /mark/geo`
- **Request Payload:** JSON object with data
  - `accuracy`
  - `jwtToken` : payload contains `did`
  - `latitude`
  - `longitude`
  - `version`
- **Response:** Status 200 if successful else 400+.

#### Mark by BSM

- **Endpoint:** `POST /mark/bsm/`
- **Request Payload:** JSON object with data
  - `mail`
  - `status`
  - `class_id`
- **Response:** Status 200 if successful.

#### Mark by Bluetooth Token

- **Endpoint:** `POST /mark/bluetooth`
- **Request Payload:** JSON object with data
  - todo
- **Response:** Status 200 if successful.

### 2. Retrieve Classes:

All api's accepts both get and post. POST request accepts `did` in param and adds user related details to the class returned by get call.

#### All Classes for Today:

##### Retrieve Class List

- **Endpoint:** `GET /classes/today`
- **Description:** Returns a list of class objects for the current day.
- **Response:** JSON array containing class objects:
  ```json
  [
    {
      "name": "Class 101",
      "class_start_time": "HH:mm:ss",
      "class_end_time": "HH:mm:ss",
      "is_attendance_mandatory": true
    },
    // Additional class objects...
  ]
  ```

##### Get All class for a particular date

- **Endpoint:** `GET /classes/<date>`
- **Description:** Returns a list of class objects for the particular day.
- **Response:** JSON array containing class objects:
  ```json
  [
    {
      "name": "Class 101",
      "class_start_time": "HH:mm:ss",
      "class_end_time": "HH:mm:ss",
      "is_attendance_mandatory": true
    },
    // Additional class objects...
  ]
  ```

##### Retrieve Class List with Attendance status

* **Endpoint:** `POST /classes/today`
* **Description:** Get attendance for classes today.
* **Request Payload:** JSON object with student token (`did`):

#### Get Current Active Class

- **Endpoint:** `GET /classes/current`
- **Response:** JSON object with details of the active class.
- **Response:** JSON array containing class objects:

```json
[
  {
    "name": "Class 101",
    "class_start_time": "HH:mm:ss",
    "class_end_time": "HH:mm:ss",
    "is_attendance_mandatory": true,
    "status": "present",
  },
  // Additional class objects...
]

```

#### Get All Attendance for a Class

- **Endpoint:** `GET /attendance/class/{classId}`
- **Response:** HTML page with attendance details for the specified class.

### 3. Verification:

#### Verify Mark by Geo Location

- **Endpoint:** `GET /verify/geo/{falseAttemptId}`
- **Description:** Verify the mark by geo location for the given `falseAttemptId`.
- **Permissions:** Only users with the permission `can_verify_false_attempt` can access this endpoint.
- **Response:** Status 200 if verification is successful.

### 4. Notifications:

#### Send Notification to student

- **Endpoint:** `POST /notifications/student/{id}`
- **Description:** Send a notification to a specific student.
- **Request Payload:** JSON object with notification details (title, message).
- **Response:** Status 200 if successful.

#### Send Notification to All Absentees of a Class

- **Endpoint:** `POST /notifications/class/{classId}/absentes`
- **Description:** Send a notification to all absentees of a specific class.
- **Request Payload:** JSON object with notification details (e.g., message).
- **Response:** Status 200 if successful.

```json
{
  "message": "Sent to 61 students",
  "sent_to": [studentName1, studentName2 ...]
}

```

Given that there are specific caches to delete, let's update the Cache Management section to include individual cache deletion endpoints:

### Cache Management:

**Permission:** Should be a `staff` user

#### Delete Home Page Cache

- **Endpoint:** `DELETE /caches/clear_get_current_class`
- **Description:** Delete the cache for the home page.
- **Response:** Status 200 if the home page cache is successfully deleted.

#### Delete "Get Current Class Attendance" Cache

- **Endpoint:** `DELETE /caches/clear_get_current_class_attendance`
- **Description:** Delete the cache for the "Get Current Class Attendance" operation.
- **Response:** Status 200 if the cache is successfully deleted.

#### Delete "Get Today's Classes" Cache

- **Endpoint:** `DELETE /caches/clear_get_todays_classs`
- **Description:** Delete the cache for the "Get Today's Classes" operation.
- **Response:** Status 200 if the cache is successfully deleted.

### Additional Considerations:

- Consider adding error handling and appropriate status codes for each endpoint.
- Ensure proper validation of input data to prevent potential security vulnerabilities.

This design provides a RESTful structure with clear endpoints for each functionality. Adjustments can be made based on specific requirements and any additional features needed for the application.
