FROM python:3.10

ENV PYTHONUNBUFFERED 1

# Install Chrome
RUN apt-get update \
  && apt-get install -y \
  chromium \
  && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \
    && curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin

# Install additional dependencies
RUN apt-get install -y libnss3 \
    && apt-get install -y libgconf-2-4

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--", "--no-sandbox", "--disable-dev-shm-usage"]

