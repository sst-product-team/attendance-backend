# attendance-backend

## Code contribution

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

After that you have to create superuser and create some dummy data.
Dummy data can be created using django Fixtures if you are interested raise a PR for that.

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
