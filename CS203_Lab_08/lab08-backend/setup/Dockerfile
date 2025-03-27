FROM python:3.9-alpine

WORKDIR /app

COPY requirements-setup.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY setup.py ./setup.py

CMD ["python", "setup.py"]
