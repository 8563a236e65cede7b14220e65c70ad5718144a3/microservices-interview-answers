# Build a base Debian image
docker image build -t base_debian -f base_debian .

# Build the nameko base image
docker image build -t nameko_base -f nameko_base .

# Compile app base
docker image build -t app_base -f app_base .

# Create the interview-net network
docker network create --driver bridge interview-net

# Start rabbitmq instance on interview-net
docker run -d --network interview-net --publish 5672:5672 \
  --publish 15672:15672 --name rabbitmq_interview rabbitmq

# Start nameko_base container
docker run -it --network interview-net \
 --name interview app_base

nameko shell
#b = ["abc", "def", "ghi"]
#