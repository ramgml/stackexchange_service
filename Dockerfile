FROM python:3.8

EXPOSE 8080

WORKDIR /web

ENV PYTHONPATH "${PYTHONPATH}:/web"

COPY . /web

RUN pip install pipenv

COPY Pipfile Pipfile.lock /web/

RUN pipenv install --system

CMD ["python", "app/main.py"]
