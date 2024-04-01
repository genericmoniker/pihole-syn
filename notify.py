"""Send notifications for blocked DNS lookups."""

import datetime
import io
import logging
import smtplib

import mailer


logger = logging.getLogger(__name__)


def notify(config, entries):
    """Send a notification for each blocked domain."""

    for entry in entries:
        request_time = datetime.datetime.fromtimestamp(entry.timestamp)
        logger.info(
            "Upstream block at %s: %s, client=%s",
            request_time,
            entry.domain,
            entry.client,
        )

    try:
        with _configure_smtp(config) as client:
            mail = mailer.Mailer(client)
            mail.send_message(
                config.MAIL_RECIPIENTS,
                config.MAIL_SENDER,
                "DNS Block",
                _render_message_body(entries),
            )
    except Exception:
        logger.exception("Error sending mail.")


def _configure_smtp(config):
    client = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
    client.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
    return client


def _render_message_body(entries):
    buffer = io.StringIO()
    print("DNS lookup(s) blocked by upstream sever:", file=buffer)
    print(file=buffer)
    for entry in entries:
        logger.debug("Entry: %s", entry)
        request_time = datetime.datetime.fromtimestamp(entry.timestamp)
        print("-", request_time, entry.domain, f"(from {entry.client})", file=buffer)
    print(file=buffer, flush=True)
    body = buffer.getvalue()
    logger.debug("Message: %s", body)
    return body


# Entry point for testing notifications without running the main application:
if __name__ == "__main__":
    from config import Config
    from pihole import Entry

    config = Config()
    entry = Entry(1, 1250000, 7, "foo.bar", "1.2.3.4")
    notify(config, [entry])
