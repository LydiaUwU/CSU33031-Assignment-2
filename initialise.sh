# Initialisation script
# TODO: Make this prettier
# TODO: Router initialisation and connection

# Variables
subnet=172.20.0.0/16

# Create Network
echo -e "\n🌐 Creating network"
sudo docker network create -d bridge --subnet $subnet a2-network

# Copy tools.py to directories
cp tools.py endpoint/
cp tools.py router/

# Create router
sudo docker build -t a2-router ./router
sudo docker container create --name a2-router --cap-add=ALL a2-router
sudo docker network connect a2-network a2-router

# Create Endpoints
sudo docker build -t a2-endpoint ./endpoint

# remove tools.py from directories
rm endpoint/tools.py
rm router/tools.py