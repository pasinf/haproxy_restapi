#!/bin/bash
# Copyright 2013 Prashanth Hari
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
