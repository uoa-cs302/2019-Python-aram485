import json
import urllib
import nacl.pwhash
import cherrypy
from constants import Constants
import minions
import nacl.encoding
import nacl.signing
import nacl.secret
import socket
import time
import base64
import datetime

const = Constants()


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
local_ip_address = s.getsockname()[0]

def getReportedUsers(username):
    apikey = minions.get_api_key(username)
    x_header = minions.create_x_header(username, apikey)
    res = minions.read_responseH(const.getURL() + "/list_users", None, x_header)
    return res


def load_new_apikey(username, password):
    header = minions.create_BASIC_auth_header(username, password)
    url = const.getURL() + "/load_new_apikey"
    res = minions.read_response(url, None, header)
    if type(res) is dict:
        return res["api_key"]
    else:
        raise cherrypy.HTTPError(401, message="Invalid Credentials")


def loginserver_pubkey(username):
    # GET function
    apikey = minions.get_api_key(username)
    x_header = minions.create_x_header(username, apikey)
    reponse_tuple = minions.read_response(const.getURL() + "/loginserver_pubkey", None, x_header)
    return reponse_tuple


def get_privatedata(username, password):
    # GET function
    apikey = minions.get_api_key(username)
    x_header = minions.create_x_header(username, apikey)
    password_new = 16 * password
    password_b = bytes(password_new, encoding='utf-8')
    salt = bytes(password_new.encode('utf-8')[:16])
    ops = nacl.pwhash.argon2i.OPSLIMIT_SENSITIVE
    mem = nacl.pwhash.argon2i.MEMLIMIT_SENSITIVE

    res = minions.read_response(const.getURL() + "/get_privatedata", None, x_header)
    # res = json.dumps(res)
    print("RESSSS\n\n\n:", res)
    print("RESPONSE", res)
    key = nacl.pwhash.argon2i.kdf(32, password_b, salt, ops, mem)
    box = nacl.secret.SecretBox(key)  # safe used to encrypt/decrypt messages
    print("RES: ", res)
    plaintext = box.decrypt(str(res['privatedata']), encoder=nacl.encoding.Base64Encoder)
    data = plaintext.decode('utf-8')
    print(data)
    try:
        return data
    except:
        return 0


def add_privatedata(username, password, prikeys, blocked_pubkeys, blocked_usernames, blocked_words,
                    blocked_message_signatures, favourite_message_signatures, friends_usernames):
    url = const.getURL() + "/add_privatedata"
    apikey = minions.get_api_key(username)
    x_header = minions.create_x_header(username, apikey)
    password_new = 16 * password
    password_b = bytes(password_new, 'utf-8')
    salt = bytes(password_new.encode('utf-8')[:16])
    ops = nacl.pwhash.argon2i.OPSLIMIT_SENSITIVE
    mem = nacl.pwhash.argon2i.MEMLIMIT_SENSITIVE
    key = nacl.pwhash.argon2i.kdf(32, password_b, salt, ops, mem)
    box = nacl.secret.SecretBox(key)
    print("private keys:", prikeys, "\n", "blocked pubkeys", blocked_pubkeys, "\n", "blocke uernames",
          blocked_usernames, "\n", " blocked words:", blocked_words, "\n", "blocked messages",
          blocked_message_signatures, "\n", "fave messages", favourite_message_signatures, "\n", "friendss, usernames",
          friends_usernames, "\n")
    privateData = {
        "prikeys": prikeys,
        "blocked_pubkeys": blocked_pubkeys,
        "blocked_usernames": blocked_usernames,
        "blocked_words": blocked_words,
        "blocked_message_signatures": blocked_message_signatures,
        "favourite_message_signatures": favourite_message_signatures,
        "friends_usernames": friends_usernames
    }

    privateDataJSON = json.dumps(privateData)
    privateDataJSON = bytes(privateDataJSON, encoding='utf-8')
    encrypted_data = box.encrypt(privateDataJSON, encoder=nacl.encoding.Base64Encoder)
    encoded_data = encrypted_data.decode('utf-8')
    send_time = str(time.time())
    lsr = get_loginserver_record(username)
    lsr = lsr['loginserver_record']
    privkey = minions.get_privatekey(username)
    privKeyObj = minions.convert_to_privObj(privkey)
    send_time = str(time.time())
    signature = minions.generate_signature(privKeyObj, bytes(encoded_data + lsr + send_time, encoding='utf-8'))

    data = {
        "privatedata": encoded_data,
        "loginserver_record": lsr,
        "client_saved_at": send_time,
        "signature": signature
    }

    res = minions.read_response(url, data, x_header)
    return res


def ping_check_tx(username):
    send_time = str(time.time())
    apikey = minions.get_api_key(username)
    x_header = minions.create_x_header(username, apikey)

    data = {
        "my_time": send_time,
        "connection_address": "172.23.180.241:1234",
        "connection_location": 1
    }

    allUsers = getReportedUsers(username)['users']

    for user in allUsers:
        user_addy = user['connection_address']
        url = "http://" + user_addy + "/api/ping_check"
        try:
            res = minions.read_response(url, data, x_header)
            print("Sent!")
        except ConnectionRefusedError:
            print("Connection refused")
        except TimeoutError:
            print("socket error")
        except:
            print("Didn't work due to server error!")
    return


def add_pubkey(username, api_key):
    signing_key = nacl.signing.SigningKey.generate()
    privkey_hex_str = signing_key.encode(nacl.encoding.HexEncoder).decode('utf-8')
    pubkey_hex = signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder)
    pubkey_hex_str = pubkey_hex.decode('utf-8')

    message_bytes = bytes(pubkey_hex_str + username, encoding='utf-8')
    signature_hex_str = minions.generate_signature(signing_key, message_bytes)

    data = {
        "pubkey": pubkey_hex_str,
        "username": username,
        "signature": signature_hex_str
    }

    header = minions.create_x_header(username, api_key)
    url = const.getURL() + "/add_pubkey"
    res = minions.read_response(url, data, header)
    if res["response"] == 'ok':
        return privkey_hex_str, pubkey_hex_str
    else:
        raise cherrypy.HTTPError(500, message="Internal Server Error")


def pull_privatedata(username, password):
    data = get_privatedata(username, password)
    print("\n THE DATA IS: \n", data)
    data = json.loads(data)
    minions.blockUser(username, ",".join(data['blocked_usernames']))
    minions.insert_blocked_words(username, ",".join(data['blocked_words']))
    minions.befriend(username, ",".join(data['friends_usernames']))


def push_privateData(username, password):
    blocked_words = minions.getBlockedWords(username)
    if blocked_words is None:
        blocked_words = ["", ""]
    else:
        blocked_words = blocked_words.split(",")

    blockedUsers = minions.getBlockUserList(username)
    if blockedUsers is None:
        blockedUsers = ["", ""]
    else:
        blockedUsers = blockedUsers.split(",")

    friends = minions.getFriendList(username)
    if friends == None:
        friends = ["", ""]
    else:
        friends = friends.split(",")

    privKey = minions.get_privatekey(username)
    print("SENT: ", username, password, [privKey], [], blockedUsers, blocked_words, ['hi'], ['hi'], friends)
    res = add_privatedata(username, password, [privKey], [], blockedUsers, blocked_words, ['hi'], ['hi'], friends)
    return res


def report(username, api_key, pubkey, status):
    if (status == 0):
        status = 'online'
    elif (status == 1):
        status = 'busy'
    elif (status == 2):
        status = 'away'
    else:
        status = "offline"

    data = {
        "connection_address": str(local_ip_address),
        "connection_location": 1,
        "incoming_pubkey": pubkey,
        "status": status
    }

    s = str(socket.gethostbyname(socket.gethostname()))
    print(s)

    header = minions.create_x_header(username, api_key)
    url = const.getURL() + "/report"
    res = minions.read_response(url, data, header)
    if res is not None:
        if res["response"] == 'ok':
            return
        else:
            raise cherrypy.HTTPError(500, message="Internal Server Error")


def get_loginserver_record(username):
    apikey = minions.get_api_key(username)
    x_header = minions.create_x_header(username, apikey)
    response_tuple = minions.read_response(const.getURL() + "/get_loginserver_record", None, x_header)
    return response_tuple


class MineApp(object):
    # CherryPy Configuratiousernaamen
    _cp_config = {'tools.sessions.on': True}

    # @cherrypy.expose
    # @cherrypy.config(**{'tools.cors.on': True})
    # @cherrypy.tools.json_in()
    # @cherrypy.tools.json_out()
    # def pull_data(self):
    #     username = 'aram485'
    #     pull_privatedata(username, "1245")
    #     return

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def signin(self):
        data = cherrypy.request.json
        print("DATA IS +++++++: ", data)
        username = data["username"]
        password = data["password"]
        specialKey = data["specialKey"]
        api_key = load_new_apikey(username, password)
        (private_key, public_key) = add_pubkey(username, api_key)
        report(username, api_key, public_key, 0)
        if not minions.user_exists(username):
            minions.insert_new_user(username, password, public_key, private_key, api_key)
        else:
            minions.update_user(username, public_key, private_key, api_key)
        pull_privatedata(username, specialKey)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def list_users(self):
        data = cherrypy.request.json
        username = data['username']
        res = getReportedUsers(username)
        return res

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def push_data(self):
        # data = cherrypy.request.json
        # username = data['username']
        # specialKey = data['specialKey']
        username = "aram485"
        specialKey = "1245"
        push_privateData(username, specialKey)
        return

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def ping_check(self):
        # POST
        data = cherrypy.request.json
        username = data['username']
        res = ping_check_tx(username)
        return res

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def get_broadcast(self):
        return minions.get_broadcasts()

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def tx_broadcast(self):
        # POST function
        data = cherrypy.request.json
        username = data['username']
        message = data['message']
        lsr = get_loginserver_record(username)
        lsr = lsr['loginserver_record']
        privkey = minions.sql_read("SELECT u.PrivateKey FROM AllUsers u WHERE u.Username = ?;", (username,),
                                   "BoopDB.db")
        privkey = privkey[0][0]
        privKeyObj = minions.convert_to_privObj(privkey)
        send_time = str(time.time())
        signature = minions.generate_signature(privKeyObj, bytes(lsr + message + send_time, encoding='utf-8'))

        data = {
            "loginserver_record": lsr,
            "message": message,
            "sender_created_at": send_time,
            "signature": signature
        }

        apikey = minions.get_api_key(username)
        x_header = minions.create_x_header(username, apikey)
        url = "http://" + const.getURL() + "/rx_broadcast"
        url = "http://localhost:1234/api/rx_broadcast"
        res = minions.read_response(url, data, x_header)
        print(res)

        allUsers = self.list_users()['users']

        for user in allUsers:
            user_addy = user['connection_address']
            url = "http://" + user_addy + "/api/rx_broadcast"
            print("\n", url)
            try:
                res = minions.read_response(url, data, x_header)
                print("Sent!")
            except ConnectionRefusedError:
                print("Connection refused")
            except TimeoutError:
                print("socket error")
            except:
                print("Didn't work due to server error!")
            # print(res)
        return

        # allUsers = {
        #     "users" : {
        #         "user1" : {
        #         "connection_location" : "172.23.88.17:1337",
        #         "connection_address" : "2"
        #     }}
        # }
        # for user in allUsers['users']:
        #     print(user)
        # if user["connection_location"] == '2':
        #     try:
        #         url = "http://" + user["connection_address"] + "/api/rx_broadcast"
        #         print(url)
        #         req = urllib.request.Request(url, data=data, headers=x_header)
        #         response = urllib.request.urlopen(req)
        #         json_response = json.loads(response.read().decode('utf-8'))
        #         print(json_response)
        #         print("--------------------------------")
        #         response.close()  # be a tidy kiwi
        #     except:
        #         pass

        # res = minions.read_response(const.getURL() + "/rx_broadcast", data, x_header)
        # return res

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def tx_privateMessage(self):
        data = cherrypy.request.json
        username = data['username']
        message = data['message']
        sendToUser = data['sendToUsername']
        message_bytes = bytes(data['message'], 'utf-8')
        lsr = get_loginserver_record(username)
        lsr = lsr['loginserver_record']
        target_pubkey = loginserver_pubkey(username)['pubkey']
        target_pubkey_b = bytes(loginserver_pubkey(username)['pubkey'], 'utf-8')
        target_username = "admin"
        target_connection_location = "210.54.33.182:80"

        target_pubkey_b = bytes("06f486b5206210188484142cac81da5de3abde999ca199df42f1d93b012f6010", 'utf-8')
        target_username = "merw957"
        target_connection_location = "172.23.7.115:10000"

        target_pubkey_b = bytes(minions.get_pubkey(username), 'utf-8')
        target_username = "aram485"
        target_connection_location = "localhost:1234"

        allUsers = self.list_users()
        allUsers = allUsers['users']
        for user in allUsers:
            print("username: ", user['username'])
            if (user['username'] == sendToUser):
                target_pubkey_b = bytes(user['incoming_pubkey'], 'utf-8')
                target_username = sendToUser
                target_connection_location = user['connection_address']

        print(target_connection_location)
        if (target_username == None):
            return "404: Username not found"

        print("TARGETTTTTT: ", target_connection_location)

        privkey = minions.sql_read("SELECT u.PrivateKey FROM AllUsers u WHERE u.Username = ?;", (username,),
                                   "BoopDB.db")

        privkey = privkey[0][0]
        privKeyObj = minions.convert_to_privObj(privkey)
        send_time = str(time.time())

        verifyKey = nacl.signing.VerifyKey(target_pubkey_b, encoder=nacl.encoding.HexEncoder)
        tPubKey = verifyKey.to_curve25519_public_key()
        sealed_box = nacl.public.SealedBox(tPubKey)
        encryptedMessage = (sealed_box.encrypt(message_bytes, encoder=nacl.encoding.HexEncoder))
        e_message = encryptedMessage.decode('utf-8')
        message_bytes = bytes(lsr + target_pubkey + target_username + e_message + send_time, encoding='utf-8')
        signature = minions.generate_signature(privKeyObj, message_bytes)

        data = {
            "loginserver_record": lsr,
            "target_pubkey": target_pubkey,
            "target_username": target_username,
            "encrypted_message": e_message,
            "sender_created_at": send_time,
            "signature": signature
        }

        apikey = minions.get_api_key(username)
        x_header = minions.create_x_header(username, apikey)
        print("\n\n\n\nHEY")
        url = "http://" + target_connection_location + "/api/rx_privatemessage"
        res = minions.read_response(url, data, x_header)
        # if(res['response'] != "ok"):
        #     return "404: malfunction"
        print("\n\nRESPONSE", res, "URL", url)
        return

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def client_report(self):
        data = cherrypy.request.json
        username = data["username"]
        report(username, minions.get_api_key(username), minions.get_pubkey(username), minions.get_status(username))
        return

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def filter_by_time(self):
        time1 = "6:10,9/6/2019"
        unix1 = minions.dt_to_unix(time1)
        time2 = "5:56,1/6/2019"
        unix2 = minions.dt_to_unix(time2)
        entries = minions.filter_time(min(unix1, unix2), max(unix1, unix2))
        return (entries)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def amBusy(self):
        username = 'aram485'
        minions.update_status(username, 1)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def amAway(self):
        username = 'aram485'
        minions.update_status(username, 2)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def amOffline(self):
        username = 'aram485'
        minions.update_status(username, 3)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def amOnline(self):
        username = 'aram485'
        minions.update_status(username, 0)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def filter_by_word(self):
        data = cherrypy.request.json
        word = data['word']
        entries = minions.filter_word(word)
        return (entries)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def filter_by_sender(self):
        data = cherrypy.request.json
        sender = data['username']
        entries = minions.filter_sender(sender)
        return (entries)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def filter_by_senderPM(self):
        data = cherrypy.request.json
        sender = data['username']
        entries = minions.filter_senderPM(sender)
        return (entries)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def blockUser(self):
        data = cherrypy.request.json
        username = data["username"]
        toBlock = data["blockName"]
        user = toBlock
        currentBlockedUsers = minions.getBlockUserList(username)
        if currentBlockedUsers == None:
            currentBlockedUsers = ""
        minions.blockUser(username, currentBlockedUsers + "," + user)

    ############################################################################################################################

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getBlockedUserList(self):
        data = cherrypy.request.json
        username = data["username"]
        return minions.getBlockUserList(username)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getFriendList(self):
        data = cherrypy.request.json
        username = data["username"]
        return minions.getFriendList(username)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getWordList(self):
        data = cherrypy.request.json
        username = data["username"]
        return minions.getBlockedWords(username)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getRecentDMs(self):
        username = 'aram485'
        list1 = minions.time_ordered_PMs(username)
        return list1

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def currentlyOnline(self):
        username = 'aram485'
        users = getReportedUsers(username)['users']
        send_time = str(time.time())
        apikey = minions.get_api_key(username)
        x_header = minions.create_x_header(username, apikey)

        data = {
            "my_time": send_time,
            "connection_address": "172.23.180.241:1234",
            "connection_location": 1
        }

        usernames = []

        for user in users:
            print(user)
            user_addy = user['connection_address']
            url = "http://" + user_addy + "/api/ping_check"
            try:
                res = minions.read_response(url, data, x_header)
                print("USER IS ", usernames)
                print("Sent!")
                usernames.append(user['username'])
            except ConnectionRefusedError:
                print("Connection refused")
            except TimeoutError:
                print("socket error")
            except:
                print("Didn't work due to server error!")
        return usernames

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def friendUser(self):
        data = cherrypy.request.json
        username = data["username"]
        toFriend = data["friendName"]
        user = toFriend
        currentFriends = minions.getFriendList(username)
        if currentFriends == None:
            currentFriends = ""
        print("user", user, "currentfrineds", currentFriends)
        minions.befriend(username, currentFriends + "," + user)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def blockWords(self):
        # get data from front end, call it data
        data = cherrypy.request.json
        username = data["username"]
        blocked = data["blockedWords"].strip()
        currentBlocked = minions.getBlockedWords(username)
        if currentBlocked == None:
            currentBlocked = ""
        print(blocked)
        minions.insert_blocked_words(username, currentBlocked + "," + blocked)
        return

    # @cherrypy.expose
    # @cherrypy.config(**{'tools.cors.on': True})
    # @cherrypy.tools.json_in()
    # @cherrypy.tools.json_out()
    # def favourite(self):
    #





