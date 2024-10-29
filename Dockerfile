FROM python:3.10-alpine

WORKDIR /usr/src/app
COPY requirements.txt .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add --no-cache libpq-dev gcc python3-dev musl-dev zlib-dev libjpeg-turbo-dev cargo
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
