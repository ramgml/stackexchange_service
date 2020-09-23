FROM python:3.7

EXPOSE 8080

WORKDIR /web

ENV PYTHONPATH "${PYTHONPATH}:/web"

COPY . /web

RUN pip install pipenv

COPY Pipfile Pipfile.lock /web/

RUN pipenv install --system

RUN chmod +x wait-for-it.sh

RUN chmod +x entrypoint.sh