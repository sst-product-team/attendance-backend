# Attendance Backend

## Frontend Mobile App

If you're looking for the mobile app that complements this backend, check out our [Mobile App](https://github.com/sst-product-team/attendance-app/releases/). It provides a user-friendly interface for managing attendance and viewing reports.

## Preview
Students attendance report  [page](https://attendancebackend-v9zk.onrender.com/attendance/studentAttendance/kushagra.23bcs10165/)
<div style="display: flex; justify-content: space-between;">
  <img width="1421" alt="Screenshot 2024-01-16 at 12 56 03 AM" src="https://github.com/sst-product-team/attendance-backend/assets/39624018/4edff32f-69d1-4c2b-988f-f2ef8a443c94">
</div>

## Code contribution

## Setup

### Using python.

Make sure that you have +python3.8 installed.

```bash
pip install -r ./requirements.txt
```

For sure you will get some errors after running above step fix those and then continue.

```bash
python manage.py makemigrations
python manage.py makemigrations attendance
python manage.py migrate
python manage.py runserver
```

After that you can load dummy data. Run below command in a different shell.
```bash
python manage.py loaddata ./fixture.json
```

### Lint & Formatting
We use `flake8==6.1.0` as a linter and `black==23.11.0` as a code formatter

Install
```bash
pip install flake8==6.1.0 black==23.11.0
```

Run black
```bash
black .
```

Run flake8
```bash
flake8 .
```

### To build an image.
```bash
docker build -t attendance-backend .
```

### To run the container and listen on localhost.
```bash
docker run --network=host attendance-backend
```

Now you can access the server at `http://localhost:8000`

if anything is missed visit [docker-cheetsheet](https://docs.docker.com/get-started/docker_cheatsheet.pdf)

## To run test file

### To run all test
```bash
python manage.py test
```
### To run a specific testfile
```bash
python manage.py test attendance.test.models.test_classattendancewithgeolocationTest
```
