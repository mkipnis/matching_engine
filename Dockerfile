FROM python:3.13-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps (cache-friendly)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app
COPY liquibook_sandbox.py .
COPY components ./components
COPY liquibook_adapter ./liquibook_adapter

# Expose port (Dash default)
EXPOSE 8050

CMD ["python", "liquibook_sandbox.py"]
