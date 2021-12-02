# Launch endpoint (the command is a lil obtuse by default)
# Author: Lydia MacBride

sudo docker container run -it --net=a2-network"$1" --hostname=a2-endpoint"$2" a2-endpoint