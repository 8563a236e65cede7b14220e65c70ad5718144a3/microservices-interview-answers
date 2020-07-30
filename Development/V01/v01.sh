# Build a base Debian image
docker image build -t base_debian -f base_debian .

# Build the nameko base image
docker image build -t nameko_base -f nameko_base .

# Compile app base
docker image build -t app_base -f app_base .

#
nameko run invictus.service --config config.yaml