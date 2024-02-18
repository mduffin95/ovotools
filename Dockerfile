FROM cyrilix/numpy:latest
#LABEL authors="matthew"

RUN mkdir /app
WORKDIR /app

#RUN pip install --upgrade pip
#RUN apt-get update
#RUN apt-get -y upgrade
#RUN apt-get -y install cmake

#RUN pip install --upgrade setuptools wheel
#RUN pip install numpy
RUN pip install matplotlib ovoenergy

#ADD requirements.txt .
#RUN pip install -r requirements.txt

ADD *.py .
CMD ["python", "./main.py"]