FROM python:3.7

ADD . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app/app.py"]
