# Expenses

To run the app in production use the following command:

```
uwsgi  --master \
        --socket 0.0.0.0:3031 \
        --protocol uwsgi \
        --plugins python3 \
        --wsgi-file wsgi.py \
        --callable app \
        --processes 4 \
        --threads 2 \
        --env APP_CONFIG=production \
        --enable-threads
```

A couple of notes:

- `--enable-threads` is for Sentry and New Relic support
- `--env APP_CONFIG=production` can take a value of `{development, staging, production}` depending on the required context
