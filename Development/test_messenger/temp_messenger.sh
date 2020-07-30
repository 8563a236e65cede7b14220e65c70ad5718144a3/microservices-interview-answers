# Create nameko_base_messenger image from
# nameko_base
docker image build -t nameko_base_messenger .

# Create the interview-net network
docker network create --driver bridge interview-net

# Check that network has been created
docker network ls

# Start rabbitmq instance on interview-net
docker run -d --network interview-net --publish 5672:5672 \
  --publish 15672:15672 --name rabbitmq_interview rabbitmq

# Start redis server
docker run -d --network interview-net  \
  --publish 6379:6379 --name redis_interview redis

# Check that both are running
docker ps

# Start nameko_base container
docker container run -it \
  --name driver_interview --network interview-net \
  nameko_base_messenger /bin/bash

# Change to app folder
cd app

# Remove invictus folder
rm -rf invictus

# Compile requirements
pip-compile requirements/base.in
pip-compile requirements/test.in

# Run messenger service
nameko run temp_messenger.service --config config.yaml &
