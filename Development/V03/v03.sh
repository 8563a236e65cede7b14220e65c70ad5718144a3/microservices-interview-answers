# Create pika_python image for microservices base
docker image build -t pika_python -f pika_python .

# Create the interview-net network
docker network create --driver bridge interview-net

# Start rabbitmq instance on interview-net
docker container run -d --network interview-net --publish 5672:5672 \
  --publish 15672:15672 --name rabbitmq_interview rabbitmq

# Start a Pika server container
docker container run -it --network interview-net \
  --name pika_python pika_python

# Open a new terminal and run the client
python client.py
