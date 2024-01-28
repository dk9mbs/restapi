import datetime
import requests
import json

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log, jsontools
from shared.model import *

import imaplib
import email
from email.header import decode_header
import os

import email

logger=log.create_logger(__name__)

def execute(context, plugin_context, params):
    postboxes=api_email_mailbox.objects(context).select().where(api_email_mailbox.type_id=='IMAP'). \
        where(api_email_mailbox.is_enabled==-1).to_list()

    for postbox in postboxes:
        process_imap(context, postbox.id.value, postbox.imap_server.value, 
            postbox.imap_folder.value, postbox.username.value, postbox.password.value)

def process_imap(context, mailbox_id, imap_server, folder, username, password):
    now=datetime.datetime.now()

    def clean(text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)

    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)

    status, messages = imap.select(folder)
    # number of top emails to fetch
    #N = 1
    # total number of emails
    #messages = int(messages[0])

    status, messages = imap.search(None, '(UNSEEN)')
    messages=[int(s) for s in messages[0].split()]

    #for i in range(messages, messages-N, -1):
    for i in messages:
        #print(f"################{i} ")
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    encoding=_get_encoding(encoding)
                    subject = subject.decode(encoding)
                # decode email sender
                msg_from=_get_header_value(msg, "From")
                msg_to=_get_header_value(msg, "To", "")
                msg_id=_get_header_value(msg, "Message-ID")
                msg_spam_level=_get_header_value(msg, "X-Spam-Level", "")

                print("subject:", subject)
                print("from:", msg_from)

                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            #print(body)
                            pass
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                #open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    #body = msg.get_payload(decode=True).decode()
                    body=str(msg.get_payload(decode=True), str("utf-8"), "ignore").encode('utf8', 'replace')
                    if content_type == "text/plain":
                        # print only text email parts
                        #print(body)
                        pass

                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        #os.mkdir(folder_name)
                        pass

                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    #open(filepath, "w").write(body)
                    # open in the default browser
                    #webbrowser.open(filepath)
                    mail=api_email()
                    mail.mailbox_id.value=mailbox_id
                    mail.message_id.value=msg_id
                    mail.subject.value=subject.encode('utf-8').decode('utf-8')
                    #mail.body.value=body
                    mail.message_from.value=msg_from
                    mail.message_to.value=msg_to
                    mail.insert(context)


                print("="*100)
    # close the connection and logout
    imap.close()
    imap.logout()

"""
default:None raise an exception in case of not exists key
"""
def _get_header_value(msg, key, default=None):
    value, encoding = decode_header(msg.get(key, ""))[0]
    if isinstance(value, bytes):
        encoding=_get_encoding(encoding)
        value = value.decode(encoding)
    return value
    

def _get_encoding(encoding):
    if encoding==None:
        return "latin-1"
    elif encoding=="unknown-8bit":
        return "iso-8859-1"
    else:
        return encoding
    