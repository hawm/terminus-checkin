FROM python:3.10-slim AS dep
COPY requirements.txt ./
RUN pip install -r requirements.txt -q --root-user-action=ignore \
    --no-cache-dir --disable-pip-version-check \
    --target=/appdeps
ENV PYTHONPATH="${PYTHONPATH}:/appdeps"

FROM dep AS src
COPY . /app

FROM src AS prod
WORKDIR /app
VOLUME /app/sessions
ENTRYPOINT [ "bash", "./entrypoint.sh" ]

FROM mcr.microsoft.com/vscode/devcontainers/python:3.10 AS dev
COPY --from=prod /appdeps /appdeps
ENV PYTHONPATH="${PYTHONPATH}:/appdeps"
