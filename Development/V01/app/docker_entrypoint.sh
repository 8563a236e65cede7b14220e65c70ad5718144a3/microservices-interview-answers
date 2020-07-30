# Build config file dynamically
echo -n "AMQP_URI: \"pyamqp://guest:guest@" > config.yaml

# Get the ip address of the rabbitmq instance
echo "$(dig +short rabbitmq_interview)\"" >> config.yaml
echo "rpc_exchange: \"nameko-rpc\"" >> config.yaml

# Run the service
nameko run invictus.service --config config.yaml
