# gpg-mailgate

gpg-mailgate is a content filter for Postfix that automatically encrypts unencrypted incoming email using PGP for select recipients.

For installation instructions, please refer to the included INSTALL file.

# Features
- Correctly displays attachments and general email content; currently will only display first part of multipart messages
- Public keys can be stored in a dedicated gpg-home-directory (see Note 1 in INSTALL)
- Encrypts both matching incoming and outgoing mail (this means gpg-mailgate can be used to encrypt outgoing mail for software that doesn't support PGP)
- Easy installation

This is forked from the original project at http://code.google.com/p/gpg-mailgate/

# Authors

This is a combined work of many developers:

* mcmaster <mcmaster@aphrodite.hurricanelabs.rsoc>
* Igor Rzegocki <ajgon@irgon.com> - [GitHub](https://github.com/ajgon/gpg-mailgate)
* perennate <admin@perennate.com> - [GitHub](https://github.com/uakfdotb/gpg-mailgate)
* Colin Moller <colin@unixarmy.com> - [GitHub](https://github.com/LeftyBC/gpg-mailgate)
* Taylor Hornby <havoc@defuse.ca> - [GitHub](https://github.com/defuse/gpg-mailgate)
* Martin (uragit) <uragit@telemage.com> - [GitHub](https://github.com/uragit/gpg-mailgate)
