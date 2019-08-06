FROM python:3.7-alpine

RUN apk update \
    && apk add --no-cache bash \
    && apk add gcc \
    && apk add musl-dev \
    && apk add linux-headers \
    && apk add jpeg-dev \
    && apk add zlib-dev \
    && apk add mariadb-dev \
    && apk add libffi-dev \
    && apk add libxml2-dev \
    && apk add libxslt-dev \
    && apk add python-dev


# install pypi packages
COPY pip-requirements.txt /requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm /usr/bin/mysql*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]