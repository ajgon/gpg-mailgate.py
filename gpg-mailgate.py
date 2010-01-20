#!/usr/bin/python

from ConfigParser import RawConfigParser
import email
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
to_addrs = map(lambda x: x.strip(), raw_message['To'].split(','))
if raw_message.has_key('Cc'):
	to_addrs.extend( map(lambda x: x.strip(), raw_message['Cc'].split(',')))
if raw_message.has_key('Bcc'):
	to_addrs.extend( map(lambda x: x.strip(), raw_message['Bcc'].split(',')))

def send_msg( message, recipients = None ):
	if recipients == None:
		recipients = to_addrs
	relay = (cfg['relay']['host'], int(cfg['relay']['port']))
	smtp = smtplib.SMTP(relay[0], relay[1])
	smtp.sendmail( from_addr, recipients, message.as_string() )
	sys.exit(0)

gpg_to = list()
keys = GnuPG.public_keys( cfg['gpg']['keyhome'] )
for to in to_addrs:
	domain = to.split('@')[1]
	if domain in cfg['default']['domains'].split(','):
		if to in keys:
			gpg_to.append( (to, to) )
		elif cfg.has_key('keymap') and cfg['keymap'].has_key(to):
			gpg_to.append( (to, cfg['keymap'][to]) )

if gpg_to == list():
	if cfg['default'].has_key('add_header') and cfg['default']['add_header'] == 'yes':
		raw_message['X-GPG-Mailgate'] = 'Not encrypted, public key not found'
	send_msg( raw_message )

if raw_message.is_multipart():
	payload = list()
	for part in raw_message.get_payload():
		if part.get_content_type() == "text/plain":
			payload.append(part)
	raw_message.set_payload( payload )

if cfg.has_key('logging') and cfg['logging'].has_key('file'):
	log = open(cfg['logging']['file'], 'a')
	log.write("Encrypting email to: %s\n" % ' '.join( map(lambda x: x[0], gpg_to) ))
	log.close()

if cfg['default'].has_key('add_header') and cfg['default']['add_header'] == 'yes':
	raw_message['X-GPG-Mailgate'] = 'Encrypted by GPG Mailgate 0.1'

gpg = GnuPG.GPGEncryptor( cfg['gpg']['keyhome'], map(lambda x: x[1], gpg_to) )
gpg.update( raw_message.get_payload() )
raw_message.set_payload( gpg.encrypt() )
send_msg( raw_message, map(lambda x: x[0], gpg_to) )
