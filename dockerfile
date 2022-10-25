FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt -q --no-cache-dir --disable-pip-version-check

COPY . . 

VOLUME /app/sessions

ENTRYPOINT [ "bash", "./entrypoint.sh" ]