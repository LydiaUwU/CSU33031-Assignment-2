# Initialisation script
# TODO: Router initialisation and connection

# Variables
subnet0=172.20.0.0/16
subnet1=172.30.0.0/16
subnet2=172.40.0.0/16
subnet3=172.50.0.0/16
subnet4=172.60.0.0/16
subnet5=172.70.0.0/16
subnet6=172.80.0.0/16
subnet7=172.90.0.0/16

# Create Networks
echo -e "\n🌐 Creating networks"
sudo docker network create -d bridge --subnet $subnet0 a2-network0
sudo docker network create -d bridge --subnet $subnet1 a2-network1
sudo docker network create -d bridge --subnet $subnet2 a2-network2
sudo docker network create -d bridge --subnet $subnet3 a2-network3
sudo docker network create -d bridge --subnet $subnet4 a2-network4
sudo docker network create -d bridge --subnet $subnet5 a2-network5
sudo docker network create -d bridge --subnet $subnet6 a2-network6
sudo docker network create -d bridge --subnet $subnet7 a2-network7

# Copy tools.py to directories
echo -e "\n👾 Copying tools library to subdirectories"
cp tools.py controller/
cp tools.py endpoint/
cp tools.py router/

# Create Controller
echo -e "\n🎮 Creating controller image and containers"
sudo docker build -t a2-controller ./controller
sudo docker container create --name a2-controller --cap-add=ALL a2-controller
sudo docker network connect a2-network0 a2-controller
sudo docker network connect a2-network1 a2-controller
sudo docker network connect a2-network2 a2-controller
sudo docker network connect a2-network3 a2-controller
sudo docker network connect a2-network4 a2-controller
sudo docker network connect a2-network5 a2-controller
sudo docker network connect a2-network6 a2-controller
sudo docker network connect a2-network7 a2-controller
sudo docker network disconnect bridge a2-controller

# Create router
echo -e "\n🚅 Creating router image and containers"
sudo docker build -t a2-router ./router

# Router 0
sudo docker container create --name a2-router0 --cap-add=ALL a2-router
sudo docker network connect a2-network0 a2-router0
sudo docker network connect a2-network1 a2-router0
sudo docker network disconnect bridge a2-router0

# Router 1
sudo docker container create --name a2-router1 --cap-add=ALL a2-router
sudo docker network connect a2-network1 a2-router1
sudo docker network connect a2-network2 a2-router1
sudo docker network connect a2-network4 a2-router1
sudo docker network disconnect bridge a2-router1

# Router 2
sudo docker container create --name a2-router2 --cap-add=ALL a2-router
sudo docker network connect a2-network2 a2-router2
sudo docker network connect a2-network3 a2-router2
sudo docker network disconnect bridge a2-router2

# Router 3
sudo docker container create --name a2-router3 --cap-add=ALL a2-router
sudo docker network connect a2-network2 a2-router3
sudo docker network connect a2-network5 a2-router3
sudo docker network disconnect bridge a2-router3

# Router 4
sudo docker container create --name a2-router4 --cap-add=ALL a2-router
sudo docker network connect a2-network5 a2-router4
sudo docker network connect a2-network6 a2-router4
sudo docker network disconnect bridge a2-router4


# Create Endpoint image, must be launched with run command
echo -e "\n💫 Creating endpoint image"
sudo docker build -t a2-endpoint ./endpoint

# remove tools.py from directories
echo -e "\n🖌 Cleaning up"
rm controller/tools.py
rm endpoint/tools.py
rm router/tools.py