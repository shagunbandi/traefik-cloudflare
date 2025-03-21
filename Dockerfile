FROM python:3.9-slim

WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the script and .env file
COPY update_dns.py .
COPY .env /app/.env

# Create the log file
RUN touch /var/log/cron.log

# Create the cron job
RUN echo "*/5 * * * * cd /app && /usr/local/bin/python /app/update_dns.py >> /var/log/cron.log 2>&1" > /etc/cron.d/dns-update-cron
RUN chmod 0644 /etc/cron.d/dns-update-cron
RUN crontab /etc/cron.d/dns-update-cron

# Create the entrypoint script
RUN echo "#!/bin/sh\ncron && tail -f /var/log/cron.log" > /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"] 