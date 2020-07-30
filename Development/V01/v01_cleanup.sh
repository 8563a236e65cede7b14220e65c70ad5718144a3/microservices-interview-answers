# Cleanup containers
docker container rm -f interview rabbitmq_interview

# Cleanup network
docker network rm interview-net