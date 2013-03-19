#!/usr/bin/python
'''
API for managing HA Proxy configurations

Capabilities -
* Add Server
* Delete Server
* Disable Server
* Enable Server


Author : Prashanth Hari
Email  : prashanth_hari@cable.comcast.com

Revision History
~~~~~~~~~~~~~~~
Initial Release Date:03-19-2013

'''

from functools import wraps
from flask import Flask, request, Response, jsonify
import os
import shutil
import datetime
import commands
import ConfigParser


CONFIG_DIR = '/etc/haproxy/'
CONFIG_BAK_DIR = '/var/tmp/haproxy/'
HAPROXY_SOCKET = '/var/run/haproxy.sock'


if not os.path.isdir(CONFIG_BAK_DIR):
    os.mkdir(CONFIG_BAK_DIR)


app = Flask(__name__)
app.config['DEBUG'] = True


def readconfig():
    config = ConfigParser.SafeConfigParser()
    cf = '/var/www/haproxy/api_auth.conf'
    if ( os.path.isfile( cf ) ):
        config.readfp( open(cf) )

    try:
        user = config.get("GLOBAL","user")
        password = config.get("GLOBAL","pass")
        return {"user": user, "password": password}
    except Exception, e:
        print 'Error Reading Configuration File: %s ' % e
        sys.exit(1)


def check_auth(username, password):
    cred = readconfig()
    return username == cred['user'] and password == cred['password']

def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="haproxy"'

    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth: 
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate("Authentication Failed.")
        return f(*args, **kwargs)

    return decorated


def checkRuleExists(file_name, text):
    data = open(file_name).read()
    if text in data:
        return True
    else:
        return False


def deleteRule(file_name, match_string):
    output = open(file_name).readlines()
    f = open(file_name, 'w')
    f.writelines([item for item in output if match_string not in item])
    f.close()


def doConfigBackup(config_file):
    src = CONFIG_DIR + config_file
    config_file_bak = config_file + '-' +  datetime.datetime.today().strftime("%Y%m%d%H%M%S")
    dst = CONFIG_BAK_DIR + config_file_bak
    shutil.copy2(src, dst)

def disableServer(backend, server):
    disable_cmd = '''echo disable server %s/%s | sudo socat stdio %s''' % (backend, server, HAPROXY_SOCKET)
    try:
        cmdout = commands.getoutput(disable_cmd)
        return cmdout
    except Exception, e:
        return 'Error disabling server - %s' % e

def enableServer(backend, server):
    enable_cmd = '''echo enable server %s/%s | sudo socat stdio %s''' % (backend, server, HAPROXY_SOCKET)
    try:
        cmdout = commands.getoutput(enable_cmd)
        return cmdout
    except Exception, e:
        return 'Error disabling server - %s' % e

def reloadService():
    reload_cmd = '''sudo /etc/init.d/haproxy reload''' 
    try:
        cmdout = commands.getoutput(reload_cmd)
        return cmdout
    except Exception, e:
        return 'Error disabling server - %s' % e


'''
Post /addserver
~~~~~~~~~~~~~

:addServer - POST Format 

{
"frontend": {
        virtual_name: "XRE",
        virtual_ip: "60.60.60.60",
        virtual_port: "80"
        },
"backend": {
    real_port: "8080",
    real_servers: [
        {
            name: "xre_vm_1",
            ip: "1.1.1.1"
            },
        {
            name: "xre_vm_2",
            ip: "2.2.2.2"
            }
        ]
      }
}
'''

@app.route('/addServer', methods=['POST'])
@requires_auth
def post_data():
    if request.method == 'POST':
        front_end = request.json["frontend"]
        back_end = request.json["backend"]

        virtual_name = front_end['virtual_name']
        virtual_ip = front_end['virtual_ip']
        virtual_port = front_end['virtual_port']

        real_servers = {}
        for vals in back_end['real_servers']:
            name = vals['name']
            ip = vals['ip']
            real_servers[name] = ip
            
        real_port =  back_end['real_port']

        config_file_name = '''/etc/haproxy/%s.cfg''' % virtual_name
        rules = []
    
        for server in real_servers:
            ip = real_servers[server]
            server_rule = '''server %s %s:%s check inter 2000 rise 2 fall 5 \n''' % (server, ip, real_port)
            rules.append(server_rule)

        create_rule = ''
        new_config = False
        if not os.path.exists(config_file_name):
            new_config = True
            create_rule = '''listen %s %s:%s
  balance roundrobin
  option  tcpka
  option  tcplog \n''' % (virtual_name, virtual_ip, virtual_port)

        '''Backup current configs'''
        if new_config == False:
            config_file = '''%s.cfg''' % virtual_name
            doConfigBackup(config_file) 
        
        f = open(config_file_name, "a")
        f.write(create_rule)

        for server_rule in rules:
            if not checkRuleExists(config_file_name, server_rule):
                f.write(server_rule)
        f.close()

        reloadService()
            
        return "Updated !!!"


'''
Post /deleteServer
~~~~~~~~~~~~~

:deleteServer - POST Format 

{
    "virtual_name": "XRE",
    real_servers: [
        {
            name: "xre_vm_1",
            ip: "1.1.1.1"
            },
        {
            name: "xre_vm_2",
            ip: "2.2.2.2"
            }
        ] 
    real_port: "8080",
}
'''

@app.route('/deleteServer', methods=['POST'])
@requires_auth
def post_deleteserver():
    if request.method == 'POST':
        
        virtual_name = request.json["virtual_name"]
        real_servers_post = request.json["real_servers"]
        real_port = request.json["real_port"]
        config_file_name = '''/etc/haproxy/%s.cfg''' % virtual_name
        
        real_servers = {}
        for vals in real_servers_post:
            name = vals['name']
            server_rule = '''server %s ''' % (name)
            config_file = '''%s.cfg''' % virtual_name
            doConfigBackup(config_file) 
	     
            print server_rule
            deleteRule(config_file_name, server_rule)

        reloadService()

        return "Deleted :%s" % server_rule


'''
Post /setServerMaint
~~~~~~~~~~~~~~~~

:setServerMaint - POST Format

{
    virtual_name: "XRE",
    real_servers: ["xre_vm_1", "xre_vm_2"]
}

'''

@app.route('/setServerMaint', methods=['POST'])
@requires_auth
def post_setservermaint():
    if request.method == 'POST': 
        virtual_name = request.json["virtual_name"]
        real_servers = request.json["real_servers"]

        for server in real_servers:
            cmdout = disableServer(virtual_name, server)
            
        return cmdout


'''
Post /unsetServerMaint
~~~~~~~~~~~~~~~~

:unsetServerMaint - POST Format

{
    virtual_name: "XRE",
    real_servers: ["xre_vm_1", "xre_vm_2"]
}

'''

@app.route('/unsetServerMaint', methods=['POST'])
@requires_auth
def post_unsetservermaint():
    if request.method == 'POST': 
        virtual_name = request.json["virtual_name"]
        real_servers = request.json["real_servers"]

        for server in real_servers:
            cmdout = enableServer(virtual_name, server)
            
        return cmdout



if __name__ == '__main__':
    app.run(host="0.0.0.0")
