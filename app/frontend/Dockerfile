FROM python:3.12-slim

WORKDIR /app

# 1. Copy ONLY requirements.txt to cache this layer
COPY requirements.txt .

# 2. Install dependencies 
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy frontend source files
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]