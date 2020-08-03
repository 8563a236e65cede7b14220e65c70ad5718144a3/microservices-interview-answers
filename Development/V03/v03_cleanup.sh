# Cleanup containers
docker container rm -f pika_python rabbitmq_interview

# Cleanup network
docker network rm interview-net

# Cleanup images
docker image rm pika_python