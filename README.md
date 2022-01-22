# pihole-syn

My setup for running  Pi-Hole on a Synology NAS using Docker Compose.

This includes a custom notifier application that can send an email alert when
there is a DNS lookup block from the *upstream* DNS server.

## Configuration

The docker-compose.yaml file has several network-specific settings that need to
be correct, and those are commented as such in the file. You'll also need to
map volumes to existing directories on the NAS.

For the notifier, settings use Docker secrets. Create a `secrets` directory
with a notifier_config.json file something like this:

```json
{
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_USERNAME": "my@gmail.com",
    "SMTP_PASSWORD": "my password here",
    "FTL_DB_FILE": "/etc/pihole/pihole-FTL.db",
    "MAIL_SENDER": "my@gmail.com",
    "MAIL_RECIPIENTS": "me@somewhere.com"
}
```

For Pi-Hole itself, the compose file references secrets/pihole.env, so you can
pu the WEBPASSWORD environment variable in there.

## Running or updating

1. ssh to the device using the admin account.
2. switch to root with `sudo -i`
3. change to the directory containing this repo.
4. `docker-compose pull`
5. `docker-compose build`
6. `docker-compose up --detach`
