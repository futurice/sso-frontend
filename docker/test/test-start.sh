
sed -i "s/DOMAIN/${DOMAIN}/" /etc/nginx/nginx.conf
sed -i "s#SOCKET_IO_ADDR#${SOCKET_IO_ADDR}#" /etc/nginx/nginx.conf
sed -i "s#SOCKET_IO_SCHEME#${SOCKET_IO_SCHEME}#" /etc/nginx/nginx.conf
sed -i "s/DOMAIN/${DOMAIN}/" /opt/static/js/login_ping.js
sed -i "s/SCHEME/${SCHEME}/" /opt/static/js/login_ping.js
sed -i "s#SOCKET_IO_ADDR#${SOCKET_IO_ADDR}#" /opt/static/js/socket.js
sed -i "s#SCHEME#${SCHEME}#" /opt/static/js/socket.js


service postgresql start
./sso_frontend/manage.py migrate --noinput

/usr/bin/supervisord -c /etc/supervisor/test-supervisord.conf &

sleep 10

# run casperjs tests
./sso_frontend/manage.py loaddata sso_frontend/login_frontend/fixtures/casper.json
./node_modules/casperjs/bin/casperjs test --verbose --loglevel=debug casper_smoketests

#run some django tests
./sso_frontend/manage.py test sso_frontend/login_frontend