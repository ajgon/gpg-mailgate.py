#!/usr/bin/python

from ConfigParser import RawConfigParser
import email
import email.message
import re
import GnuPG
import smtplib
import sys

# Read configuration from /etc/gpg-mailgate.conf
_cfg = RawConfigParser()
_cfg.read('/etc/gpg-mailgate.conf')
cfg = dict()
for sect in _cfg.sections():
	cfg[sect] = dict()
	for (name, value) in _cfg.items(sect):
		cfg[sect][name] = value

# Read e-mail from stdin
raw = sys.stdin.read()
raw_message = email.message_from_string( raw )
from_addr = raw_message['From']
to_addrs = list()
encrypted_to_addrs = list()
if raw_message.has_key('To'):
	to_addrs.extend( [e[1] for e in email.utils.getaddresses([raw_message['To']])] )
if raw_message.has_key('Cc'):
	to_addrs.extend( [e[1] for e in email.utils.getaddresses([raw_message['Cc']])] )
if raw_message.has_key('Bcc'):
	to_addrs.extend( [e[1] for e in email.utils.getaddresses([raw_message['Bcc']])] )
if raw_message.has_key('X-GPG-Encrypt-To'):
        tmp_list = list()
        tmp_list.extend( [e[1] for e in email.utils.getaddresses([raw_message['X-GPG-Encrypt-To']])] )
        encrypted_to_addrs.extend( [e for e in tmp_list if e in to_addrs] )
        for eaddr in encrypted_to_addrs:
                if eaddr in to_addrs:
                        to_addrs.remove( eaddr )
if raw_message.has_key('X-GPG-Encrypt-Cc'):
        encrypted_to_addrs.extend( [e[1] for e in email.utils.getaddresses([raw_message['X-GPG-Encrypt-Cc']])] )

def send_msg( message, recipients = None ):
	if recipients == None:
		return
	if cfg.has_key('logging') and cfg['logging'].has_key('file'):
		log = open(cfg['logging']['file'], 'a')
		log.write("Sending email to: <%s>\n" % '> <'.join( recipients ))
		log.close()
	relay = (cfg['relay']['host'], int(cfg['relay']['port']))
	smtp = smtplib.SMTP(relay[0], relay[1])
	smtp.sendmail( from_addr, recipients, message.as_string() )

def encrypt_payload( payload, gpg_to_cmdline ):
	gpg = GnuPG.GPGEncryptor( cfg['gpg']['keyhome'], gpg_to_cmdline )
	raw_payload = payload.get_payload(decode=True)
	gpg.update( raw_payload )
	payload.set_payload( gpg.encrypt() )
	if payload['Content-Disposition']:
		payload.replace_header( 'Content-Disposition', re.sub(r'filename="([^"]+)"', r'filename="\1.pgp"', payload['Content-Disposition']) )
	if payload['Content-Type']:
		payload.replace_header( 'Content-Type', re.sub(r'name="([^"]+)"', r'name="\1.pgp"', payload['Content-Type']) )
		if payload.get_content_type() != 'text/plain' and payload.get_content_type != 'text/html':
			payload.replace_header( 'Content-Type', re.sub(r'^[a-z/]+;', r'application/octet-stream;', payload['Content-Type']) )
			payload.set_payload( "\n".join( filter( lambda x:re.search(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$',x), payload.get_payload().split("\n") ) ) )
	return payload

def encrypt_all_payloads( payloads, gpg_to_cmdline ):
	encrypted_payloads = list()
	if type( payloads ) == str:
		msg = email.message.Message()
		msg.set_payload( payloads )
		return encrypt_payload( msg, gpg_to_cmdline ).as_string()
	for payload in payloads:
		if( type( payload.get_payload() ) == list ):
			encrypted_payloads.append( encrypt_all_payloads( payload.get_payload(), gpg_to_cmdline ) )
		else:
			encrypted_payloads.append( [encrypt_payload( payload, gpg_to_cmdline )] )
	return sum(encrypted_payloads, [])

def get_msg( message ):
	if not message.is_multipart():
		return message.get_payload()
	return '\n\n'.join( [str(m) for m in message.get_payload()] )

keys = GnuPG.public_keys( cfg['gpg']['keyhome'] )
gpg_to = list()
ungpg_to = list()
for enc in encrypted_to_addrs:
	domain = enc.split('@')[1]
	if domain in cfg['default']['domains'].split(','):
		if enc in keys:
			gpg_to.append( (enc, enc) )
                elif cfg.has_key('keymap') and cfg['keymap'].has_key(enc):
                        gpg_to.append( (enc, cfg['keymap'][enc]) )
			
for to in to_addrs:
	domain = to.split('@')[1]
	if domain in cfg['default']['domains'].split(','):
		if to in keys:
			gpg_to.append( (to, to) )
		elif cfg.has_key('keymap') and cfg['keymap'].has_key(to):
			gpg_to.append( (to, cfg['keymap'][to]) )
	else:
		ungpg_to.append(to)

if gpg_to == list():
	if cfg['default'].has_key('add_header') and cfg['default']['add_header'] == 'yes':
		raw_message['X-GPG-Mailgate'] = 'Not encrypted, public key not found'
	send_msg( raw_message )
	exit()

if ungpg_to != list():
	send_msg( raw_message, ungpg_to )

if cfg.has_key('logging') and cfg['logging'].has_key('file'):
	log = open(cfg['logging']['file'], 'a')
	log.write("Encrypting email to: %s\n" % ' '.join( map(lambda x: x[0], gpg_to) ))
	log.close()

if cfg['default'].has_key('add_header') and cfg['default']['add_header'] == 'yes':
	raw_message['X-GPG-Mailgate'] = 'Encrypted by GPG Mailgate'

gpg_to_cmdline = list()
gpg_to_smtp = list()
for rcpt in gpg_to:
	gpg_to_smtp.append(rcpt[0])
	gpg_to_cmdline.extend(rcpt[1].split(','))

encrypted_payloads = encrypt_all_payloads( raw_message.get_payload(), gpg_to_cmdline )
raw_message.set_payload( encrypted_payloads )

send_msg( raw_message, gpg_to_smtp )
