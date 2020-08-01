# Build alpine development image
docker image build -t alpine_build -f alpine_build .

# Build RabbitMQ development environment
docker image build -t rabbitmq_build -f rabbitmq_build .

# Build the production rabbitmq_c client base image
docker image build -t rabbitmq_c -f rabbitmq_c_client .

#Build rabbitmq_c_app
docker image build -t rabbitmq_c_app -f rabbitmq_c_app .