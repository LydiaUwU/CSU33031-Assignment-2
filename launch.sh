# Script to launch non endpoint devices
# Author: Lydia MacBride

echo -e "š Launching components"

# Launch server
echo -e "\nš¦ Launching controller"
# sudo docker container start a2-controller

# Launch sensors
echo -e "\nš Launching routers"
# sudo docker kill $(sudo docker container ls -q)
sudo docker container start $(sudo docker container ls -a -q -f name="a2-router*") > /dev/null
