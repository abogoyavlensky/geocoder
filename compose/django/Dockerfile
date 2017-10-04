FROM python:3.6-alpine3.6

ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Moscow

LABEL org.label-schema.maintainer="Andrey Bogoyavlensky"
LABEL org.label-schema.description="Base image for service app"

COPY ./requirements.txt /requirements.txt

# Install build deps, then run `pip install`, then remove unneeded build deps.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            build-base \
            libffi-dev \
    && pip install --no-cache-dir -r /requirements.txt \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /user/local \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

WORKDIR /app
