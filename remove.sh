# Short removal script
# Author: Lydia MacBride

# TODO: Make it so this doesnt nuke all the user's containers and images

sudo docker kill $(sudo docker container ls -q)
sudo docker container prune
sudo docker image prune