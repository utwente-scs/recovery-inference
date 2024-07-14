FROM python:3.10-bullseye

WORKDIR /app
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=1

RUN apt-get -y update

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade wheel
RUN pip install pipenv

RUN pip install Flask

RUN pip install -U spacy
RUN python -m spacy download en_core_web_trf

RUN pip install iocsearcher

EXPOSE 5000

CMD ["flask", "run"]
