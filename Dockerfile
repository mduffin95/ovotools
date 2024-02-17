FROM python:3.11
LABEL authors="matthew"

RUN mkdir /app
WORKDIR /app

ADD *.py .
ADD requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "./main.py"]