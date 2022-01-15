# notifier dockerfile

# I think pi-hole is using bullseye, so hopefully some shared layers.
FROM python:3.9-slim-bullseye

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

RUN pip install --user --upgrade pip
RUN pip install --user smtplib

COPY . .

# Install the app itself.
RUN /home/appuser/.local/bin/poetry install --no-dev -v

CMD ["/home/appuser/.local/bin/poetry", "run", "python", "-m", "dnsreport"]
