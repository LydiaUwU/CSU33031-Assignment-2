# CSU33031-Assignment-2
My implementation for CSU33031 Computer Networks assignment 2

Please see the included PDF CSU33031_Assignment_2_Report.pdf for an in depth look at the design and implementation for this assignment.

Link to Github repo in case you are viewing a download of this: https://github.com/LydiaUwU/CSU33031-Assignment-2

## Setup
To setup the example network run `./setup.sh`, the controller and created routers can then be launched with `.\launch.sh`.

Once the controller is running you can then run `./endpoint.sh <network_number> <endpoint_number>` to create and connect to a new endpoint device.

## Usage
For information on the available commands while using an endpoint please run `help`.

## Removal
Either remove the containers, images and networks manually (preferable if you have any of these that you wish to keep) or run `./remove.sh`