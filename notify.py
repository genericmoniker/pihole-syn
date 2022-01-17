import datetime
import logging


# TODO: Temporary...
try:
    import smtplib
except ImportError:
    pass


logger = logging.getLogger(__name__)


def notify(config, entries):
    for entry in entries:
        request_time = datetime.datetime.fromtimestamp(entry.timestamp)
        logger.info(
            "Upstream block at %s: %s, client=%s",
            request_time,
            entry.domain,
            entry.client,
        )


def _configure_smtp(config):
    client = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
    client.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
    return client
