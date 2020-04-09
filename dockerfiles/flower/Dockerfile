FROM python:3.6
# Install the required packages
RUN pip install redis flower

COPY ./backend/requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1

# Default port
EXPOSE 5555

# Run as a non-root user by default, run as user with least privileges.
USER nobody

ENTRYPOINT ["flower"]