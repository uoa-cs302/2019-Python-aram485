from constants import Constants
import minions
import cherrypy
import nacl.encoding
import nacl.signing
import sqlite3
import json
import socket
import time

x_header = None
header = None
usernameCurrent = None
const = Constants()


class MainApp(object):

    # CherryPy Configuration
    _cp_config = {'tools.encode.on': True,
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on': 'True',
                  }


    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def rx_broadcast(self):
        username = 'aram485'
        received = cherrypy.request.json
        print(received)
        
        print("Sender:", received["loginserver_record"])
        login_list = (received["loginserver_record"].split(","))
        sender_name = login_list[0]
        sender_pubkey = login_list[1]
        send_time = login_list[2]
        sender_signature = received["signature"]
        sender_created_at = received["sender_created_at"]

        message = received.get('message')
        censored = minions.processBlockedWords(username, message)
        if(minions.sender_in_blacklist('aram485', sender_name)):
            censored = "BLOCKED"
            print(censored)
            return "Error 400: This user is blocking you"
        print(censored)

        timerec  = str(time.time())
        minions.insert_broadcast(timerec, sender_name, censored)

        response = {
            'response':'ok'
        }
        response = json.dumps(response)
        return (response)


    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def rx_privatemessage(self):
        received = cherrypy.request.json

        #Everything between here and en_message is to display who it is, and needs clean up
        print("DM Sender:", received["loginserver_record"])
        login_list = (received["loginserver_record"].split(","))
        sender_name = login_list[0]
        sender_pubkey = login_list[1]
        send_time = login_list[2]
        sender_signature = received["signature"]
        sender_created_at = received["sender_created_at"]

        encrypted_message = received['encrypted_message'].encode('utf-8')
        me = received['target_username']
        print(me)

        privkey = minions.get_privatekey(me)
        print(privkey)

        privKeyObj = minions.convert_to_privObj(privkey)
        pubkey = privKeyObj.to_curve25519_private_key()

        sealed_box = nacl.public.SealedBox(pubkey)
        decrypted = sealed_box.decrypt(encrypted_message, encoder=nacl.encoding.HexEncoder).decode('utf-8')

        censored = minions.processBlockedWords(me, decrypted)
        minions.insert_PM(me, sender_name, censored)

        response = {
            'response':'ok'
        }

        if(minions.sender_in_blacklist(me, sender_name)):
            censored = "A blocked user is trying to contact you. Don't worry you are protected"
            print(censored)
            return "Error 400: This user is blocking you"
        
        print("DECRYPTED: ", censored)

        response = json.dumps(response)
        return (response)
    
    @cherrypy.expose 
    def test(self):
        return "hi"

    @cherrypy.expose
    def ping_check(self):
        send_time = str(time.time())
        data = {
            "response" : "ok",
            "my_time" : send_time   
        }
        response = json.dumps(data)
        return response