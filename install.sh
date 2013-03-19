#!/bin/bash


##Install all dependent packages
apt-get install python-setuptools -y
easy_install flask

apt-get install haproxy -y
apt-get install apache2 -y
apt-get install libapache2-mod-wsgi -y


## Post Install
sed -i s/ENABLED=0/ENABLED=1/ /etc/default/haproxy
sed -i s/Listen\ 80/Listen\ 5000/ /etc/apache2/ports.conf
a=$(hostname) ; sed -i s/local_host_name/$a/ haproxy_api.conf
cp haproxy_api.conf /etc/apache2/conf.d/
mkdir /var/www/haproxy
cp haproxy_api.py api_auth.conf haproxy.wsgi /var/www/haproxy
cp haproxy.cfg /etc/haproxy
cp haproxy_init /etc/init.d/haproxy
chmod +x /etc/init.d/haproxy
chmod 0777 /etc/haproxy
/etc/init.d/apache2 restart
/etc/init.d/haproxy restart
