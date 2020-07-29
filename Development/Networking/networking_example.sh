# Using user-defined bridges

# Check existing networks
docker network ls

# Create the alpine-net network
docker network create --driver bridge alpine-net

# Check that the network was create successfully
docker network ls

# Inspect the alpine-net network
docker network inspect alpine-net

# Create containers in different configurations
docker run -dit --name alpine1 --network alpine-net alpine ash
docker run -dit --name alpine2 --network alpine-net alpine ash
docker run -dit --name alpine3 alpine ash
docker run -dit --name alpine4 --network alpine-net alpine ash
docker network connect bridge alpine4

# Verify that all containers are running
docker container ls

# Inspect the bridge network and the alpine-net network again
docker network inspect bridge | jq
docker network inspect alpine-net | jq

# Attach to container 1
docker container attach alpine1
# ping -c 2 alpine2
# ping -c 2 alpine4
# ping -c 2 alpine1
# ping -c 2 alpine3

# Attach to container 4
docker container attach alpine4
# ping -c 2 alpine1
# ping -c 2 alpine2
# ping -c 2 alpine3
# ping -c 2 172.17.0.2
# ping -c 2 alpine4
# ping -c 2 google.com

# Stop and remove all containers and the alpine-net network
docker container stop alpine1 alpine2 alpine3 alpine4
docker container rm alpine1 alpine2 alpine3 alpine4
docker network rm alpine-net
