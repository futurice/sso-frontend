FROM sso-frontend

RUN npm install phantomjs-prebuilt slimerjs casperjs coffee-script
RUN apt-get install -y postgresql libpq-dev

ENV PHANTOMJS_EXECUTABLE /opt/app/node_modules/phantomjs-prebuilt/bin/phantomjs
ENV FAKE_TESTING true
ENV DEBUG true
ENV PUBTKT_PUBKEY /opt/app/docker/test/test-pubtktkey
ENV SAML_PUBKEY /opt/app/docker/test/test-samlkey

ENV DB_HOST ''
ENV DB_USER ''
ENV DB_PASSWORD ''
ENV SEND_EMAILS false

USER postgres
RUN service postgresql start && psql --command 'CREATE USER root;' && createdb -O root login && psql --command 'ALTER USER root CREATEDB;'
USER root

COPY test-supervisord.conf /etc/supervisor/test-supervisord.conf

RUN /opt/app/node_modules/coffee-script/bin/coffee -c casper_smoketests/*.coffee
RUN rm casper_smoketests/*.coffee

#RUN rm sso_frontend/login_frontend/migrations/00*
#RUN rm sso_frontend/cspreporting/migrations/00*

CMD bash -C '/opt/app/docker/test/test-start.sh'