FROM python:3.6.3
ENV PYTHONUNBUFFERED 1
ADD backend/worker-requirements.txt /worker-requirements.txt
RUN pip install -r /worker-requirements.txt
HEALTHCHECK CMD celery inspect ping -A app -d celery@$HOSTNAME