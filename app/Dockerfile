FROM python:3.12-slim

WORKDIR /app

# System deps voor PyMuPDF en MySQL
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create upload and pdf dirs
RUN mkdir -p /app/uploads /app/pdfs /app/spell_images

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
