FROM python:3.8.18-bookworm

WORKDIR /attendance-backend

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD [ "python3","manage.py","runserver"]