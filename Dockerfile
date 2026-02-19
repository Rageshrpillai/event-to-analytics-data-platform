#FETCHING BASE DOCKER IMAGE

FROM python:3.10-slim

#Disabeling python Buffer lag and Python cache write on disk
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# ---  Work Directory ---
# This creates a folder inside the container called "/app".
WORKDIR /app


# Install Dependencies (The "Caching" Layer)
# Docker skips this slow "pip install" step. This saves minutes on every build.
COPY requirements.txt .
#dont save the global pip install files in my container
RUN pip install --no-cache-dir -r requirements.txt

#Copy applocation code
# Now  copy everything else (ingestion/, warehouse/, config.py, etc.)
# Because of .dockerignore, the venv and .env are NOT copied here.
COPY  . .


# Create Non-Root User
RUN useradd -m appuser && \
    chown -R appuser:appuser  /app
USER appuser


# 7. Default Command (Will be overridden by Compose)
CMD ["python", "ingestion/src/main.py"]