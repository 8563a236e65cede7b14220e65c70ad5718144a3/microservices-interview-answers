# Build a base Debian image
docker image build -t base_debian -f base_debian .

# Start container
docker container run -it base_debian

# Update packages
apt-get update && apt-get upgrade -y

# Install prerequisites
apt-get install -y apt-transport-https curl libreadline7 gnupg \
    libterm-readline-gnu-perl libterm-readline-perl-perl

# Add rabbitmq signing key
curl -fsSL \
    https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc | \
    apt-key add - \

# Add RabbitMQ and Erlang repositories to apt sources
echo "deb https://dl.bintray.com/rabbitmq-erlang/debian buster erlang" >> /etc/apt/sources.list
echo "deb https://dl.bintray.com/rabbitmq/debian buster main" >> /etc/apt/sources.list

# Refresh packages
apt-get update && apt-get upgrade -y

# Install RabbitMQ and Erlang
apt-get install -y --fix-missing rabbitmq-server erlang-base \
    erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
    erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
    erlang-runtime-tools erlang-snmp erlang-ssl \
    erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

# Workaround for lack of systemd
service cron start && service exim4 start && service rabbitmq-server start

# Install Python, Pip and Redis
apt-get install -y python3.7 python3-pip redis

# Start Redis daemon
service redis-server start

# Install Nameko, pip-tools, Redis, Jinja2
pip3 install pip-tools nameko redis jinja2

# Make application directory
mkdir app && cd app