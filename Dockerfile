# Stage 1: Build stage
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Uncomment psycopg2-binary in requirements for the build if needed
# But since we are using binary in the original requirements, it should be fine.
# Note: I'll actually uncomment it here specifically for the docker build if I could, 
# but I'll just assume the requirements.txt I wrote earlier (with it commented out)
# needs it for production. 
# Wait, I'll update requirements.txt to have it UNCOMMENTED so Docker can use it, 
# and I'll just handle local dev differently.

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose the port
EXPOSE 8000

# Entrypoint script or CMD
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn TaskAssign.wsgi:application --bind 0.0.0.0:$PORT
