1) Ensure that GPG is installed and configured.
	a) Make sure public keys for all of your potential recipients are
	   available in the GPG home directory you use in step 2
2) Configure /etc/gpg-mailgate.conf based on the provided sample config
3) Place gpg-mailgate.py in /usr/local/bin/
4) Place the GnuPG directory in /usr/lib/python2.7/ (replace 2.7 with your Python version)
5) Add the following to the end of /etc/postfix/master.cf

gpg-mailgate	unix	-	n	n	-	-	pipe
	flags= user=nobody argv=/usr/local/bin/gpg-mailgate.py ${recipient}

127.0.0.1:10028	inet	n	-	n	-	10	smtpd
	-o content_filter=
	-o receive_override_options=no_unknown_recipient_checks,no_header_body_checks
	-o smtpd_helo_restrictions=
	-o smtpd_client_restrictions=
	-o smtpd_sender_restrictions=
	-o smtpd_recipient_restrictions=permit_mynetworks,reject
	-o mynetworks=127.0.0.0/8
	-o smtpd_authorized_xforward_hosts=127.0.0.0/8

6) Add the following to /etc/postfix/main.cf

content_filter = gpg-mailgate

7) Restart postfix.

Note 1: it is also possible to create a dedicated user to store the PGP public keys

	1) useradd -s /bin/false -d /var/gpg -M gpgmap
	2) mkdir -p /var/gpg/.gnupg
	3) chown -R gpgmap /var/gpg
	4) chmod 700 /var/gpg/.gnupg
	5) sudo -u gpgmap /usr/bin/gpg --import /home/youruser/public.key --homedir=/var/gpg/.gnupg
		a) replace the path with the location of your public key
		b) the path can be deleted after importation
	6) Confirm that it's working: sudo -u gpgmap /usr/bin/gpg --list-keys --homedir=/var/gpg/.gnupg
	7) Use keyhome = /var/gpg/.gnupg in gpg-mailgate.conf
