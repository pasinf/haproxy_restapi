Overview
========

HA Proxy is a software load balancer solution in Linux and provides the features as in Hardware Load Balancer.
The application by default uses config files to manage the loadbalancer settings.

Built a set of REST API to manage the load balancer configurations which makes it easier to deploy in cloud. 

The application is currently tested only in Ubuntu. This can be made compatible with other distributions with minor changes.


Features
========

- Following features are supported
* Add Server to HA Proxy
* Delete Server from HA Proxy
* Disable Server in HA Proxy
* Enable Server in HA Proxy

- Uses Basic Authentication for REST Operations
- Username and Password are stored in config file. This might change in the future versions.
- The service listens on HTTP 5000


Dependencies and Requirements
=============================

- The application is tested only in Ubuntu Linux
- HA Proxy needs to be installed
- Apache with mod_wsgi

Installation
============

	root@test-haproxy-api:/home/ubuntu# tar -zxvf haproxy_api.tar.gz 
	root@test-haproxy-api:/home/ubuntu# cd haproxy/
	root@test-haproxy-api:/home/ubuntu/haproxy# ./install.sh 


