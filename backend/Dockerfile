FROM python:3.12-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source
COPY backend/src ./src
COPY backend/.env* ./

# Expose port (Render will pass PORT env var at runtime)
EXPOSE 8000

# Run the app (Render sets PORT, defaults to 8000)
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:${PORT:-8000} --workers 4"]
