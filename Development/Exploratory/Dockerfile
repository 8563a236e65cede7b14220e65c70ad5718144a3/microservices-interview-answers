FROM debian:latest
RUN apt-get update && apt-get upgrade -y \
    && \
    apt-get install -y apt-transport-https curl libreadline7 gnupg \
    libterm-readline-gnu-perl libterm-readline-perl-perl \
    && \
    curl -fsSL \
    https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc | \
    apt-key add - \
    && \
    echo "deb https://dl.bintray.com/rabbitmq-erlang/debian buster erlang" >> /etc/apt/sources.list \
    && \
    echo "deb https://dl.bintray.com/rabbitmq/debian buster main" >> /etc/apt/sources.list \
    && \
    apt-get update && apt-get upgrade -y \
    && \
    apt-get install -y --fix-missing rabbitmq-server erlang-base \
        erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
        erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
        erlang-runtime-tools erlang-snmp erlang-ssl \
        erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl \
    && \
    service cron start && service exim4 start \
    && \
    apt-get install -y python3.7 python3-pip redis \
    && \
    pip3 install pip-tools nameko redis jinja2 \
    && mkdir app

COPY app /app
