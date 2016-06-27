# !/bin/bash
# regex settings
sed -i "s/DOMAIN/${DOMAIN}/" /etc/nginx/nginx.conf
sed -i "s#SOCKET_IO_ADDR#${SOCKET_IO_ADDR}#" /etc/nginx/nginx.conf
sed -i "s#SOCKET_IO_SCHEME#${SOCKET_IO_SCHEME}#" /etc/nginx/nginx.conf
sed -i "s/DOMAIN/${DOMAIN}/" /opt/static/js/login_ping.js
sed -i "s/SCHEME/${SCHEME}/" /opt/static/js/login_ping.js
sed -i "s#SOCKET_IO_ADDR#${SOCKET_IO_ADDR}#" /opt/static/js/socket.js
sed -i "s#SCHEME#${SCHEME}#" /opt/static/js/socket.js
