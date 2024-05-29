FROM python:latest

RUN mkdir /app

WORKDIR /app

RUN mkdir -p screenshots/decoded \
    mkdir -p logs

COPY . /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["pytest", "-vvvsq", "--headless"]