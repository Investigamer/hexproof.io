FROM python:3.12.5-bookworm

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy to /app and set working directory
COPY . /app/.
WORKDIR /app

# Move entrypoint, install pipx
RUN mv docker/entrypoint.sh entrypoint.sh && rm -rd docker && \
    python -m pip install --user pipx && \
    python -m pipx ensurepath

# Add pipx to PATH
ENV PATH=/root/.local/bin:$PATH

# Install poetry and project
RUN pipx ensurepath && \
    pipx install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--reload", "--workers", "1", "--timeout", "60"]
