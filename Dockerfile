FROM python:3.6
COPY . /var/sender
RUN cd /var/sender && pip install -r requirements.txt