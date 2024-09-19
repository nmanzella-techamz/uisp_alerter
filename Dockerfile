FROM python:3.12.4-alpine3.20

WORKDIR /code

COPY ./code/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./code/app /code/app

WORKDIR /code/app

CMD ["python3", "/code/app/main.py"]