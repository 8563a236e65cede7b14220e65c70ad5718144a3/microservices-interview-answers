# Cleanup containers
docker container rm -f interview rabbitmq_interview

# Cleanup network
docker network rm interview-net

# Cleanup images
docker image rm base_debian nameko_base app_base