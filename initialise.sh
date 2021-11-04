# Initialisation script
# TODO: Make this prettier

# Variables
subnet=172.20.0.0/16

# Create Network
echo -e "\n🌐 Creating network"
sudo docker network create -d bridge --subnet $subnet a2-network

# Copy tools.py to directories
cp tools.py endpoint/

# Create Endpoints
sudo docker build -t a2-endpoint ./endpoint

# remove tools.py from directories
rm endpoint/tools.py