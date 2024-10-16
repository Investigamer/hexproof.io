FROM python:3.12.5-bookworm

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Update, install and configure system dependencies
RUN apt update && apt install dos2unix -y && \
    python -m pip install --user pipx && \
    pipx install poetry && \
    poetry config virtualenvs.create false

# Copy to /app and set working directory
COPY . /app/.
WORKDIR /app

# Move and convert entrypoint, remove docker, install project
RUN mv /app/docker/entrypoint.sh /app/entrypoint.sh &&  \
    dos2unix /app/entrypoint.sh && \
    rm -rd docker && \
    poetry install --without dev

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--reload", "--workers", "4", "--timeout", "60"]
