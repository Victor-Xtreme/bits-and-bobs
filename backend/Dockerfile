FROM python:3.12-slim

WORKDIR /app

# Copy requirements (Render's root is set to backend/)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source
COPY src ./src
COPY .env* ./

# Expose port
EXPOSE 8000

# Run the app (Render sets PORT, defaults to 8000)
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:${PORT:-8000} --workers 4"]
