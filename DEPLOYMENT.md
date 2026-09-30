# Deployment Guide

This application handles sensitive health-related information. Treat the production deployment as a private data system, not a public demo.

## Prepare the runtime

1. Use Python 3.12 and a production-supported MySQL 8 instance. Create a dedicated database and least-privilege database account.
2. Install the application dependencies in a clean virtual environment:

   ```sh
   python -m venv .venv
   . .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

   On Windows, activate with `.venv\\Scripts\\Activate.ps1` instead.

3. Provision the model artifact from a controlled build. Run `python train_model.py` with network access to the UCI dataset, review the resulting holdout metrics and model, and transfer `trained_model/heart_disease_model.joblib` plus `trained_model/metrics.json` to the application release. The model file must be trusted and must use the same scikit-learn version as the deployed service.

## Configure and migrate

Set these environment variables through the platform's secret manager, not a committed `.env` file:

```text
DJANGO_SECRET_KEY=<unique random secret>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=app.example.org
DB_ENGINE=mysql
DB_NAME=heart_disease
DB_USER=heart_app
DB_PASSWORD=<secret>
DB_HOST=<database host>
DB_PORT=3306
SECURE_SSL_REDIRECT=true
SECURE_HSTS_SECONDS=31536000
```

HSTS is enabled for one year by default in production mode. Confirm that every hostname covered by the policy is HTTPS-only before rollout; enable `SECURE_HSTS_INCLUDE_SUBDOMAINS` or `SECURE_HSTS_PRELOAD` only after verifying all affected hosts meet that requirement. For an initial staged rollout, set a shorter `SECURE_HSTS_SECONDS` and increase it after verification.

Then run:

```sh
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Configure the application behind a TLS-terminating reverse proxy and a production WSGI/ASGI server. Django's development server is for local use only. Serve collected static files from a web server or object store, and ensure the deployed feature-importance image is included in the static bundle if the dashboard uses it.

## Operations and safeguards

- Restrict admin and application access to authorized personnel; enforce MFA at the identity or hosting layer where available.
- Encrypt database, backups, and model artifacts at rest and in transit; test recovery from backups.
- Define consent, retention, deletion, audit, and incident-response procedures before collecting any real patient information.
- Monitor availability, error rates, database capacity, and model/version changes without logging identifiable health inputs.
- Re-evaluate the model with representative external data and clinical oversight before considering any real-world clinical use. The UCI Cleveland dataset is small and is not evidence of clinical validity.
- Review local healthcare, privacy, accessibility, and medical-device obligations with qualified counsel and clinicians.