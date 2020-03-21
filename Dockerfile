FROM node as builder

COPY . /app

WORKDIR /app
RUN npm install && npm run build:dev

# Dockerfile for Python3 on Alpine 3.9

FROM python:3.8-alpine

EXPOSE 3031

VOLUME /app

RUN apk add --no-cache --virtual build-deps gcc musl-dev \
    && apk add --no-cache --upgrade \
        jpeg-dev \
        zlib-dev \
        libffi-dev \
        cairo-dev \
        pango-dev \
        gdk-pixbuf \
        uwsgi-python3 \
        postgresql-dev \
        uwsgi

RUN adduser -s /bin/false -u 1000 -S -H app

COPY . /app

COPY --from=builder /app/app/static/dist /app/app/static/dist

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN chown -R app /app/*

USER app
WORKDIR /app
