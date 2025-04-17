FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY templates/ ./templates/

EXPOSE 9567

# Copy SSL certificates
COPY key.pem .
COPY cert.pem .
# Fix permissions so non-root user can read them
RUN chmod 644 key.pem cert.pem
# Use a non-root user for security
RUN adduser -D appuser
USER appuser

CMD ["python", "main.py"]
