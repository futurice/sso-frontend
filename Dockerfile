FROM debian:jessie
MAINTAINER Jussi Vaihia <jussi.vaihia@futurice.com>

WORKDIR /opt/app
RUN useradd -m app

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	build-essential vim htop wget \
	python python-dev python-setuptools \
	supervisor \
	git unzip \
    libpcre3 libpcre3-dev libssl-dev \
    memcached \
    libpq-dev \
    libtool libreadline6 libreadline6-dev libncurses5-dev libffi-dev \
    swig python-ldap python-dev libssl-dev \
    python-geoip libldap2-dev libsasl2-dev python-m2crypto python-mysqldb \
    redis-server libmysqlclient-dev zlib1g libjpeg-dev libpcap-dev \
    apt-utils locales

RUN apt-get update && apt-get install -y nginx-full
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

RUN mkdir /opt/static /opt/node
RUN chown -R app /opt/static/ /opt/node

RUN wget -qO /opt/node.tar.gz https://nodejs.org/dist/v0.10.40/node-v0.10.40-linux-x64.tar.gz \
    && tar xfz /opt/node.tar.gz -C /opt/node --strip-components 1 \
    && ln -s /opt/node/bin/node /usr/bin/node \
    && ln -s /opt/node/bin/npm /usr/bin/npm

RUN easy_install pip && pip install pip --upgrade
COPY requirements.txt /opt/static/requirements.txt
RUN cd /opt/static/ && pip install -r requirements.txt

RUN echo 'Europe/Helsinki' > /etc/timezone && rm /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Helsinki /etc/localtime

# Set the locale
RUN localedef -i en_US -f UTF-8 en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN mkdir -p /opt/app
RUN chown app /opt/app

# node_socket
RUN mkdir -p /opt/static/node_socket
COPY node_socket/* /opt/static/node_socket/
RUN cd /opt/static/node_socket/ && npm install

# p0f
RUN wget -qO /opt/static/p0f.tgz http://lcamtuf.coredump.cx/p0f3/releases/p0f-3.06b.tgz \
    && tar -xzvf /opt/static/p0f.tgz -C /opt/static/ && cd /opt/static/p0f-3.06b && ./build.sh
RUN useradd -m p0f
RUN mkdir /var/local/p0f

# maxmind
RUN wget -qO /opt/static/GeoLite2-City.mmdb.gz http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz
RUN cd /opt/static && gzip -d GeoLite2-City.mmdb.gz

USER app

RUN mkdir -p /opt/app/sso_frontend/data

ADD docker/supervisord.conf /etc/supervisor/supervisord.conf
ADD docker/nginx.conf /etc/nginx/nginx.conf

COPY . /opt/app/

ENV DJANGO_SETTINGS_MODULE sso_frontend.settings
ENV SECRET_KEY default_insecure_secret
ENV STATIC_ROOT "/opt/static/"
ENV LOG_DIR "/tmp/"
ENV CELERY_LOG_LEVEL WARNING
ENV TOP_DOMAIN futurice.com
ENV DOMAIN login.futurice.com
ENV SCHEME http
ENV SOCKET_IO_ADDR localhost:8080
ENV SOCKET_IO_SCHEME ws

ENV LDAP_USER_BASE_DN uid=%s,ou=People,dc=futurice,dc=com
ENV LDAP_GROUPS_BASE_DN ou=Groups,dc=futurice,dc=com

RUN python sso_frontend/manage.py collectstatic --noinput

EXPOSE 8000

USER root

CMD bash -C '/opt/app/docker/start.sh'; /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
