#!/bin/bash
#закрыть Apache2 на 80 порту
#service apache2 stop

sudo docker network create nginx_proxy
sudo docker-compose down
sudo docker-compose up -d --build
sudo docker logs nginx_proxy

sudo docker network inspect nginx_proxy

#сделать исполняемым
#chmod +x start.sh