#!/usr/bin/python3
# -*- coding: UTF-8 -*-# enable debugging

import os
os.chdir(os.path.dirname(__file__))
import bottle
import bcrypt
import time
from Crypto.Cipher import AES
from Crypto import Random
from base64 import b64decode
from base64 import b64encode
import hmac
import hashlib
import urllib.parse
import json
from bottle import route, run, template, response, redirect
from bottle.ext import beaker

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
#application = bottle.default_app()
# use beaker middleware for session handling
application = beaker.middleware.SessionMiddleware(bottle.default_app(), session_opts)

# do not cache tempaltes
bottle.debug(True)

@route('/')
def index():
    response.content_type = 'text/html; charset=utf-8'
    redirect("login")

@route('/login')
def login():
    response.content_type = 'text/html; charset=utf-8'
    
    session = bottle.request.environ.get('beaker.session')
    flash = session.get('flash','')
    session['flash'] = ''
    session.save()
    
    system = bottle.request.params.get('system',False)
    systemExists = getSystem(system)
    allSystems = getSystems()
    callback = bottle.request.params.get('callback',False)
    return template('login_template', flash=flash, callback=callback, system=system, systemExists=systemExists, allSystems=allSystems)

@route('/dologin', method='POST')
def login():
    session = bottle.request.environ.get('beaker.session')
    
    systemIdentifier = bottle.request.params.get('system',False)
    username = bottle.request.params.get('username',False)
    password = bottle.request.params.get('password',False)
    callback = bottle.request.params.get('callback',False)
    
    # only for testing
    redirectmethod = bottle.request.params.get('redirectmethod','GET')

    # TODO handle missing system, username or password
    if not systemIdentifier or not username or not password or systemIdentifier == '' or username=='' or password == '':
        response.content_type = 'text/html; charset=utf-8'
        session['flash'] = 'Missing system, username or password'
        session.save()
        redirect('login')
    
    #if not callback:
    #    response.content_type = 'text/html; charset=utf-8'
    #    session['flash'] = 'Missing callback'
    #    session.save()
    #    redirect("login")

    # to handle mising callback
    if not callback:
        callback = ''
    
    system = getSystem(systemIdentifier)
    if not system:
        response.content_type = 'text/html; charset=utf-8'
        session['flash'] = 'Unknown system'
        session.save()
        redirect('login')
    
    
    userData = validateUser(username, password)
    if not userData:
        response.content_type = 'text/html; charset=utf-8'
        session['flash'] = 'Wrong username or password'
        session.save()
        redirect('login?system=' + systemIdentifier + '&callback=' + callback)

    userDataDict = {}
    userDataDict['AUTHID'] = getMyIdentifier()
    userDataDict['SID'] = systemIdentifier
    userDataDict['AUTHID'] = getMyIdentifier()
    userDataDict['userid'] = username+"@"+getMyIdentifier()
    userDataDict['validtill'] = int(time.time())+600
    usermeta = {}
    usermeta['name'] = userData.get('name')
    usermeta['nick'] = userData.get('nick')
    usermeta['email'] = userData.get('email','')
    usermeta['name'] = userData.get('name')
    userDataDict['usermeta'] = usermeta


    sharedKeyBase64 = system.get("keybase64")
    sharedKey = b64decode(sharedKeyBase64)
    cipher=AES.MODE_CBC

    crypted = encrypt(json.JSONEncoder().encode(userDataDict), sharedKey, cipher)
    
    tokenJsonDict = {}
    tokenJsonDict['error'] = ''
    tokenJsonDict['issuer'] = getMyIdentifier()
    tokenJsonDict['crypted'] = crypted

    token = json.JSONEncoder().encode(tokenJsonDict)

    if callback == False or callback == '':
        response.content_type = 'text/html; charset=utf-8'
        return [token]
    else:
        if redirectmethod == 'NONE':
            response.content_type = 'text/plain; charset=utf-8'
            return [token+'\n\nwould redirect to'+callback]
        if redirectmethod == 'GET':
            response.content_type = 'text/plain; charset=utf-8'
            url = callback+"?token="+urllib.parse.quote(token,'')
            redirect(url)
        if redirectmethod == 'POST':
            response.content_type = 'text/html; charset=utf-8'
            markup = """
				<html>    
					<body>    
						<form action='{callback}' method='POST' name='callbackform'>    
						<input type='hidden' name='token' value='{token}'>    
						</form>    
						<script>    
							window.onload = function(){{    
							  document.forms['callbackform'].submit();    
							}}    
						</script>    
					</body>    
				</html>    
            """.format(token=token, callback=callback)
            return [markup]


    

def getMyIdentifier():
    return "SKAUTH2"

def validateUser(username, password):
    userData = getUser(username);
    if userData == False:
        return False

    pwdhash = userData.get('pwdhash')
    if bcrypt.checkpw(password.encode('utf8'), pwdhash.encode('utf8')):
        del userData['pwdhash']
        return userData
    
    return False;

def getUser(username):
    userData = {};
    # gia paragwgh pwdhash: bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
    if username == 'sk':
        userData['username'] = 'sk';
        userData['name'] = 'Stefanos';
        userData['nick'] = 'sknick';
        userData['email'] = 'sk@isc.tuc.gr';
        userData['pwdhash'] = '$2a$10$cufv/CXRZZi6Kxe2FO3bveJle0zMC0qh00lYrRY1eOE/oGEw0w0cO';
    elif username == 'sk1':
        userData['username'] = 'sk1';
        userData['name'] = 'Stefanos1';
        userData['nick'] = 'sk1nick';
        userData['pwdhash'] = '$2a$10$cufv/CXRZZi6Kxe2FO3bveJle0zMC0qh00lYrRY1eOE/oGEw0w0cO';
    elif username == 'sk2':
        userData['username'] = 'sk2';
        userData['name'] = 'Stefanos2';
        userData['nick'] = 'sk2nick';
        userData['pwdhash'] = '$2a$10$cufv/CXRZZi6Kxe2FO3bveJle0zMC0qh00lYrRY1eOE/oGEw0w0cO';
    else:
        return False
    
    return userData;

def getSystem(system):
    systems = getSystems()
    for aSystem in systems:
        identifier = aSystem.get('identifier')
        if identifier == system:
            return aSystem
    return False

def getSystems():
    systems = []
    
    system = {'identifier': 'SKSYSTEM2', 'keybase64': '7vjTsO0IhSZsNA6ze37Dk/xXw2nphFM9ZAMUkwXgaAA='}
    systems.append(system)
    
    system = {'identifier': 'SKSYSTEM3', 'keybase64': 'xxxxxxxxxxxxxxxxx'}
    systems.append(system)
    
    return systems



# START encrypt and decrypt functions
BS = AES.block_size

def pad(s):
	return s + (BS - len(s) % BS) * str_to_bytes(chr(BS - len(s) % BS))

def unpad(s):
	return s[:-ord(s[len(s)-1:])]

def str_to_bytes(data):
	u_type = type(b''.decode('utf8'))
	if isinstance(data, u_type):
		return data.encode('utf8')
	return data
	
def encrypt(plaintext, sharedKey, cipher):
	iv = Random.new().read(BS)
	encryption_suite = AES.new(sharedKey, cipher, iv)
	ciphertext_raw = encryption_suite.encrypt(pad(str_to_bytes(plaintext)))
	hmacHash = hmac.new(sharedKey, ciphertext_raw, hashlib.sha256).digest()
	ciphertext = b64encode(iv).decode("ascii") +':'+b64encode(hmacHash).decode("ascii") +':'+b64encode(ciphertext_raw).decode("ascii") 
	return ciphertext

def decrypt(ciphertext, sharedKey, cipher):
	parts = ciphertext.split(':')
	iv = b64decode(parts[0])
	hmacHash = b64decode(parts[1])
	ciphertext_raw = b64decode(parts[2])

	decryption_suite = AES.new(sharedKey, cipher, iv)
	plain_text = unpad(decryption_suite.decrypt(ciphertext_raw)).decode('utf-8')
	calcmac = hmac.new(sharedKey, ciphertext_raw, hashlib.sha256).digest()
	if hmacHash == calcmac:
		return plain_text
	else:
		return False
# END encrypt and decrypt functions
