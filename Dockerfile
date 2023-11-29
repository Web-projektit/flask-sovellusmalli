# Use Python 3.11 base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libcairo2 \
        libcairo-gobject2 \
        libffi-dev \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
# These should be adjusted according to the application's needs
ENV FLASK_APP=flask-sovellus.py \
    FLASK_ENV=production \
    SECRET_KEY=erittain_salainen_avain \
    PYDEVD_DISABLE_FILE_VALIDATION=1

# Copy the rest of your application's code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
# CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "-b", ":8000", "flask-sovellus:app"]

