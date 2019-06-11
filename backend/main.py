#!/usr/bin/python3
""" main.py

    COMPSYS302 - Software Design - Example Client Webapp
    Current Author/Maintainer: Hammond Pearce (hammond.pearce@auckland.ac.nz)
    Last Edited: March 2019

    This program uses the CherryPy web server (from www.cherrypy.org).
"""
# Requires:  CherryPy 18.0.1  (www.cherrypy.org)
#            Python  (We use 3.5.x +)

import os
import socket

import cherrypy
import mine
import server


# The address we listen for connections on
import minions

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
local_ip_address = s.getsockname()[0]

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 10051
# LISTEN_PORT = 10345
# LISTEN_IP = str(local_ip_address)


def runMainApp():

    def cors():
        if cherrypy.request.method == 'OPTIONS':
            # preflign request
            # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
            cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
            cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
            cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
            # tell CherryPy no avoid normal handler
            return True
        else:
            cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

    # set up the config
    conf = {
        '/': {
            'tools.staticdir.root': os.getcwd(),
            'tools.encode.on': True,
            'tools.encode.encoding': 'utf-8',
            'tools.sessions.on': True,
            'tools.sessions.timeout': 60 * 1,  # timeout is in minutes, * 60 to get hours
        },

    }

    cherrypy.site = {
        'base_path': os.getcwd()
    }

    cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)

    # Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
    cherrypy.tree.mount(mine.MineApp(), "/", conf)
    cherrypy.tree.mount(server.MainApp(), "/api", conf)


    # Tell cherrypy where to listen, and to turn autoreload on
    cherrypy.config.update({'server.socket_host': LISTEN_IP,
                            'server.socket_port': LISTEN_PORT,
                            'engine.autoreload.on': True,
                            })

    print("========================================")
    print("          Server is starting            ")
    print("========================================")

    # Start the web server
    cherrypy.engine.start()

    # And stop doing anything else. Let the web server take over.
    cherrypy.engine.block()


# Run the function to start everything

if __name__ == '__main__':
    minions.init_db()
    runMainApp()
