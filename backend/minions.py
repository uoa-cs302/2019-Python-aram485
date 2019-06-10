import urllib
import json
import re
import time
import datetime
import sqlite3
import nacl.encoding
import nacl.signing
import base64


def list_of_api():
    # Contains the hard coded description for evey API
    api_dict = {
        '/ping': {
            'method': 'POST',
            'requires authentication': 'Optional',
            'purpose': 'Returns an “ok” message. Use to check if the login server is online and to test your signing/authentication'
        }
    }
    return api_dict


def convert_to_json_bytes(dictionary):
    # This function returns a bit array with json thing in it. Takes in dictionary.
    return json.dumps(dictionary).encode('utf-8')


def read_response(url, data, headers):
    try:
        if (data != None):
            data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
        response = urllib.request.urlopen(req, timeout=5)
        json_response = json.loads(response.read().decode('utf-8'))
        response.close()  # be a tidy kiwi
        return json_response
    # except urllib.error.HTTPError as error:
    #     return(error)
    except TimeoutError:
        print("socket error")
    except urllib.error.HTTPError as error:
        return error
    # except:
    #     print("url error")
        # json_response = json.loads(error.read().decode('utf-8'))
        # return json_response
        # exit()

def read_responseH(url, data, headers):
    try:
        if (data != None):
            data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
        response = urllib.request.urlopen(req, timeout=0.5)
        json_response = json.loads(response.read().decode('utf-8'))
        response.close()  # be a tidy kiwi
        return json_response
    except urllib.error.HTTPError as error:
        return(error)
        # json_response = json.loads(error.read().decode('utf-8'))
        # return json_response
        # exit()


def convert_json_to_dict(data, encoding):
    # Takes in a bit array containing a json. Decodes byte into json string with encoding and then loads into dictionary
    return json.loads(data.decode(encoding))


def create_BASIC_auth_header(username, password):
    credentials = ('%s:%s' % (username, password))
    b64_credentials = base64.b64encode(credentials.encode('ascii'))
    headers = {
        'Authorization': 'Basic %s' % b64_credentials.decode('ascii'),
        'Content-Type': 'application/json; charset=utf-8',
    }
    return headers


def create_x_header(username, apikey):
    # credential_username = ('%s' % username)
    # credential_apikey = ('%s' % apikey)
    # b64_username = base64.b64encode(credential_username.encode('ascii'))
    # b64_apikey = base64.b64encode(credential_apikey.encode('ascii'))
    headers = {
        'X-username': '%s' % username,
        'X-apikey': '%s' % apikey,
        'Content-Type': 'application/json; charset=utf-8',
    }
    return headers

def processBlockedWords(username, string):
    blocking = getBlockedWords(username)
    if blocking == None:
        return  string
    t = [a for a in re.split(r'(\s|\,)', string.strip()) if a]
    # t = string.split()
    n = []
    for i in t:
        if(i in blocking):
            n.append("*"*len(i))
        else:
            n.append(i)
    return " ".join(n)

def dt_to_unix(time1):
    time1 = time1.split(",")
    hour = time1[0].split(":")[0]
    mins = time1[0].split(":")[1]
    day = time1[1].split("/")[0]
    month = time1[1].split("/")[1]
    year = time1[1].split("/")[2]
    dt = datetime.datetime(int(year), int(month), int(day), int(hour), int(mins))
    unix = time.mktime(dt.timetuple())
    return unix

def sql_commands(string, db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(string)
    conn.commit()
    conn.close()



def sql_insert(string, params, db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(string, params)
    conn.commit()
    conn.close()


def sql_read(string, params, db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(string, params)
    rows = c.fetchall()
    conn.close()
    return rows


def sql_read_single(string, db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(string)
    rows = c.fetchall()
    conn.close()
    return rows


def init_db():
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    print('Initializing Databases')
    c.execute("CREATE TABLE IF NOT EXISTS CurrentUsers("
              "Username TEXT NOT NULL UNIQUE,"
              "ApiKey TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS AllUsers("
              "ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
              "Username TEXT NOT NULL UNIQUE,"
              "Password TEXT NOT NULL,"
              "BlockedWords TEXT,"
              "BlockedUsers TEXT,"
              "Favourites TEXT,"
              "Friends TEXT,"
              "SavedPM TEXT,"
              "Status INTEGER NOT NULL,"
              "PublicKey TEXT NOT NULL,"
              "PrivateKey TEXT NOT NULL,"
              "ApiKey TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS PublicBroadcasts("
              "Time TEXT NOT NULL,"
              "Sender TEXT NOT NULL,"
              "Message TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS PrivateMessages("
              "Username TEXT NOT NULL,"
              "Sender TEXT NOT NULL,"
              "Message TEXT NOT NULL)")
    conn.commit()
    conn.close()

def insert_new_user(username, password, pubkey, privkey, apikey):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("INSERT INTO AllUsers (Username, Password, PublicKey, PrivateKey, ApiKey, Status) "
              "VALUES (?, ?, ?, ?, ?, ?)", (username, password, pubkey, privkey, apikey, 0))
    conn.commit()
    conn.close()

def insert_broadcast(time, sender, message):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("INSERT INTO PublicBroadcasts (Time, Sender, Message) "
              "VALUES (?, ?, ?)", (time, sender, message))
    conn.commit()
    conn.close()

def insert_PM(username, sender, message):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("INSERT INTO PrivateMessages (Username, Sender, Message) "
              "VALUES (?, ?, ?)", (username, sender, message))
    conn.commit()
    conn.close()

def insert_blocked_words(username, string):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("UPDATE AllUsers "
              "SET BlockedWords=?"
              "WHERE Username=?", (string, username))
    conn.commit()
    conn.close()

def update_status(username, value):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("UPDATE AllUsers "
              "SET Status=?"
              "WHERE Username=?", (value, username))
    conn.commit()
    conn.close()

def time_ordered_PMs(username):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.Sender, u.Message FROM Privatemessages u WHERE u.Username=?", (username,))
    DMs = c.fetchall()
    conn.close()
    DMs.reverse()
    return DMs
    

def get_status(username):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.Status FROM AllUsers u WHERE u.Username=?", (username,))
    status = c.fetchone()
    conn.close()
    print("STATUS  " + str(status))
    return status[0]

def get_api_key(username):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.ApiKey FROM AllUsers u WHERE u.Username=?", (username,))
    apikey = c.fetchone()
    conn.close()
    return apikey[0]

def filter_time(time1, time2):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.Sender, u.Message FROM PublicBroadcasts u WHERE u.Time BETWEEN ? AND ?;", (time1, time2))
    entries = c.fetchall()
    conn.close()
    return entries

def filter_sender(sender):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.Sender, u.Message FROM PublicBroadcasts u WHERE u.Sender=?;", (sender,))
    entries = c.fetchall()
    conn.close()
    return entries

def filter_senderPM(sender):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.Sender, u.Message FROM PrivateMessages u WHERE u.Sender=?;", (sender,))
    entries = c.fetchall()
    conn.close()
    return entries

def filter_word(word):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    string = "SELECT u.Sender, u.Message FROM PublicBroadcasts u WHERE u.Message LIKE '%{}%';".format(word)
    print(string)
    c.execute(string)
    entries = c.fetchall()
    conn.close()
    return entries
    
def getBlockedWords(username):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.BlockedWords FROM AllUsers u WHERE u.Username=?", (username,))
    blocking = c.fetchone()
    conn.close()
    realBlocked = []
    blocking_str = blocking[0]
    blocked = blocking_str.split(",")
    for blockedUser in blocked:
        if blockedUser != "":
            realBlocked.append(blockedUser)
    blocked_output = ",".join(realBlocked).split(",")
    blocked_output = ",".join(list(set(blocked_output)))
    return blocked_output

    return blocking[0]

def blockUser(username, user):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("UPDATE AllUsers "
              "SET BlockedUsers=?"
              "WHERE Username=?", (user, username))
    conn.commit()
    conn.close()

def befriend(username, user):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("UPDATE AllUsers "
              "SET Friends=?"
              "WHERE Username=?", (user, username))
    conn.commit()
    conn.close()

def getBlockUserList(username):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.BlockedUsers FROM AllUsers u WHERE u.Username=?", (username,))
    blocking = c.fetchone()
    conn.close()
    realBlocked = []
    blocking_str = blocking[0]
    blocked = blocking_str.split(",")
    for blockedUser in blocked:
        if blockedUser != "":
            realBlocked.append(blockedUser)
    blocked_output = ",".join(realBlocked).split(",")
    blocked_output = ",".join(list(set(blocked_output)))
    return blocked_output

def getFriendList(username):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT u.Friends FROM AllUsers u WHERE u.Username=?", (username,))
    friends = c.fetchone()
    conn.close()
    realFriends = []
    friends_str = friends[0]
    friends = friends_str.split(",")
    for friend in friends:
        if friend != "":
            realFriends.append(friend)
    friends_output = ",".join(realFriends).split(",")
    friends_output = ",".join(list(set(friends_output)))
    return friends_output

def update_user(username, pubkey, privkey, apikey):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("UPDATE AllUsers "
              "SET PublicKey=?, PrivateKey=?, ApiKey=?"
              "WHERE Username=?", (pubkey, privkey, apikey, username))
    conn.commit()
    conn.close()

def user_exists(username):
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM AllUsers WHERE AllUsers.Username=?", (username,))
    if len(c.fetchall()) == 1:
        conn.close()
        return True
    conn.close()
    return False

def sender_in_blacklist(username, sender):
    blocking = getBlockUserList(username)
    if blocking == None:
        return False
    blocking = blocking.split(",")
    if sender in blocking:
        return True
    else:
        return False


def generate_signature(signing_key, message_bytes):
    signed = signing_key.sign(message_bytes, encoder=nacl.encoding.HexEncoder)
    signature_hex_str = signed.signature.decode('utf-8')
    return signature_hex_str

def get_broadcasts():
    conn = sqlite3.connect("BoopDB.db")
    c = conn.cursor()
    print('getting broadcasts')
    sql_str = "SELECT * FROM PublicBroadcasts"
    c.execute(sql_str)
    entries = c.fetchall()
    return entries


def get_pubkey(username):
    pubkey = sql_read("SELECT u.PublicKey FROM AllUsers u WHERE u.Username = ?;", (username,),
                                   "BoopDB.db")
    return pubkey[0][0]

def get_privatekey(username):
    privkey = sql_read("SELECT u.PrivateKey FROM AllUsers u WHERE u.Username = ?;", (username,),
                                   "BoopDB.db")
    print(privkey)
    return privkey[0][0]

def convert_to_privObj(private_key_str):
    return nacl.signing.SigningKey(private_key_str.encode('utf-8'), encoder=nacl.encoding.HexEncoder)