# Build a base Debian image
docker image build -t nameko_temp_messenger .

# Change to app folder
cd app

# Remove invictus folder
rm -rf invictus

# Compile requirements
pip-compile requirements/base.in
pip-compile requirements/test.in
