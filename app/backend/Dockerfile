FROM python:3.12-slim

WORKDIR /app

# Install system dependencies needed for compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. Copy ONLY requirements.txt to cache this layer
COPY requirements.txt .

# 2. Install dependencies (Docker will cache this unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# 3. Finally, copy your application source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]