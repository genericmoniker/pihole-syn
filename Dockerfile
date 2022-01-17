# notifier dockerfile

# I think pi-hole is using bullseye, so hopefully some shared layers.
FROM python:3.9-slim-bullseye

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

RUN pip install --user --upgrade pip
RUN pip install --user smtplib

COPY . .

CMD ["python3", "main.py"]
