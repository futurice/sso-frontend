FROM ubuntu:14.04
MAINTAINER Jussi Vaihia <jussi.vaihia@futurice.com>

WORKDIR /opt/app
RUN useradd -m app

# Configure apt to automatically select mirror
RUN echo "deb http://fi.archive.ubuntu.com/ubuntu/ trusty main restricted universe\n\
deb http://fi.archive.ubuntu.com/ubuntu/ trusty-updates main restricted universe\n\
deb http://fi.archive.ubuntu.com/ubuntu/ trusty-security main restricted universe" > /etc/apt/sources.list

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	build-essential vim htop wget \
	python python-pip python-dev \
	supervisor \
	git unzip \
    libpcre3 libpcre3-dev libssl-dev \
    memcached \
    libpq-dev \
    libtool libreadline6 libreadline6-dev libncurses5-dev libffi-dev \
    python-pip swig python-ldap python-dev libssl-dev \
    python-geoip libldap2-dev libsasl2-dev python-m2crypto python-mysqldb \
    redis-server libmysqlclient-dev zlib1g libjpeg-dev libpcap-dev

RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62
RUN echo "deb http://nginx.org/packages/ubuntu/ trusty nginx" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

RUN mkdir /opt/static /opt/node
RUN chown -R app /opt/static/ /opt/node

RUN wget -qO /opt/node.tar.gz https://nodejs.org/dist/v4.1.1/node-v4.1.1-linux-x64.tar.gz \
    && tar xfz /opt/node.tar.gz -C /opt/node --strip-components 1 \
    && ln -s /opt/node/bin/node /usr/bin/node \
    && ln -s /opt/node/bin/npm /usr/bin/npm

COPY requirements.txt /opt/static/requirements.txt
RUN cd /opt/static/ && pip install -r requirements.txt

RUN echo 'Europe/Helsinki' > /etc/timezone && rm /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Helsinki /etc/localtime

# Set the locale
RUN locale-gen en_US.UTF-8
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
RUN wget -qO /opt/static/maxmind.gz http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz

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

RUN python sso_frontend/manage.py collectstatic --noinput

EXPOSE 8000

USER root
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
