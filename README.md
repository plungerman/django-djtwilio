django-djtwilio
=================

Django project for interacting with the Twilio API

## Build

### clean out the migrations directories

```bash
rm -rf apps/sms/migrations/
rm -rf core/migrations/
```

### migrations

```bash
python manage.py migrate
python manage.py makemigrations sms
python manage.py makemigrations core
python manage.py migrate
```

### not dependent on any other models

```bash
python manage.py loaddata core/fixtures/group.json
python manage.py loaddata apps/sms/fixtures/errors.json
python manage.py loaddata core/fixtures/account.json
python manage.py loaddata core/fixtures/user.json
```

### dependent

```bash
python manage.py loaddata apps/sms/fixtures/status.json # depends on Errors
python manage.py loaddata core/fixtures/profile.json # depends on User
python manage.py loaddata apps/sms/fixtures/message.json # depends on User
```

## Copilot

https://www.twilio.com/copilot
https://www.twilio.com/docs/sms/services/copilot-send-messages
