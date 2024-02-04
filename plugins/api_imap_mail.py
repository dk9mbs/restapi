import datetime
import requests
import json
import re, getpass
import imaplib, email
from email.header import decode_header

from core.fetchxmlparser import FetchXmlParser
from services.database import DatabaseServices
from core import log, jsontools, file as restapi_file
from shared.model import *

logger=log.create_logger(__name__)

class _FileProxy:
    def __init__(self, part):
        self._part=part

    def read(self):
        return self._part.get_payload(decode=True)

    @property
    def filename(self):
        value, encoding = decode_header(self._part.get_filename())[0]
        if type(value)==bytes:
            value=value.decode()
        return value

def execute(context, plugin_context, params):
    postboxes=api_email_mailbox.objects(context).select().where(api_email_mailbox.type_id=='IMAP'). \
        where(api_email_mailbox.is_enabled==-1).to_list()

    for postbox in postboxes:
        process_imap(context, postbox.id.value, postbox.imap_server.value, 
            postbox.imap_folder.value,postbox.imap_imported_folder.value, postbox.imap_error_folder.value, 
            postbox.imap_delete.value, postbox.username.value, postbox.password.value)

def process_imap(context, mailbox_id, imap_server, folder,folder_archive, folder_error, delete, username, password):
    now=datetime.datetime.now()

    def clean(text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)

    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, password)
    status, messages = imap.select(folder, readonly=False)
    #use not imap.search. Imap.search returns not a unique id
    status, messages = imap.uid('search', None, '(ALL)')
    #print(status)
    #print(messages)
    messages=[int(s) for s in messages[0].split()]

    for i in messages:
        print(f"Message UID: {str(i)}")
        #res, msg = imap.fetch(str(i), "(RFC822)")
        #res, msg = imap.uid('fetch', str(i), '(FLAGS BODY[HEADER.FIELDS (FROM DATE SUBJECT)])')
        res, msg = imap.uid('fetch', str(i), '(RFC822)')
        if res!="OK":
            raise Exception(f"Cannot fetch mail from imap server {str(i)}")

        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    encoding=_get_encoding(encoding)
                    subject = subject.decode(encoding)

                msg_from=_get_header_value(msg, "From")
                msg_to=_get_header_value(msg, "To", "")
                msg_id=_get_header_value(msg, "Message-ID")
                msg_spam_level=_get_header_value(msg, "X-Spam-Level", "")
                msg_delivery_date=_get_header_value(msg, "Delivery-date")
                email_parts=[]
                files=[]

                print("subject:", f"{subject}"  )

                if msg.is_multipart():
                    email_parts=[]
                    files=[]
                    body=None
                    part_body=None
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if (content_type == "text/plain" and "attachment" not in content_disposition) or content_type == "text/html":
                            part_body=str(part.get_payload(decode=True), str("utf-8"), "ignore").encode('utf8', 'replace')

                        if content_type == "text/html":
                            body=part_body
                        elif "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                #folder_name = '/tmp/test/'+clean(subject)
                                #if not os.path.isdir(folder_name):
                                #    os.mkdir(folder_name)
                                #    pass
                                #filepath = os.path.join(folder_name, filename)
                                #f=open(filepath, "wb")
                                #f.write(part.get_payload(decode=True))
                                #f.close()

                                print(f"attachment:{decode_header(filename)[0]}")
                                proxy=_FileProxy(part)
                                files.append(proxy)

                        email_part=api_email_part()
                        email_part.content_type.value=content_type
                        email_part.body.value=part_body
                        email_part.content_disposition.value=content_disposition.split(";")[0]
                        email_parts.append(email_part)

                else:
                    content_type = msg.get_content_type()
                    body=str(msg.get_payload(decode=True), str("utf-8"), "ignore").encode('utf8', 'replace')

                    if content_type == "text/plain":
                        pass

                    if content_type == "text/html":
                        pass

                mail = api_email.objects(context).select().where(api_email.message_id==msg_id).to_entity()

                if mail==None:
                    mail=api_email()
                    mail.mailbox_id.value=mailbox_id
                    mail.message_id.value=msg_id
                    mail.subject.value=subject
                    mail.body.value=body
                    mail.message_from.value=msg_from
                    mail.message_to.value=msg_to
                    mail.content_type.value=content_type
                    mail.folder.value=folder
                    mail.message_uid.value=i
                    inserted_id=mail.insert(context)

                    for key in msg.keys():
                        header=api_email_header()
                        header.email_id.value=inserted_id
                        header.header_key.value=key
                        header.header_value.value=_get_header_value(msg, key)
                        header.insert(context)

                    for email_part in email_parts:
                        email_part.email_id.value=inserted_id
                        email_part.insert(context)

                    for part in files:
                        try:
                            file=restapi_file.File()
                            #print(f"**** FILENAME****:{part.filename}")
                            file.create_file(context, part, f"email/{inserted_id}", 
                                reference_field_name="email_id", reference_id=inserted_id)
                        except Exception as e:
                            import traceback
                            traceback.print_exc()

                    result = imap.uid('COPY', str(i), folder_archive)
                    if result[0] == 'OK':
                        if delete==-1:
                            mov, data = imap.uid('STORE', str(i) , '+FLAGS', '(\Deleted)')
                        imap.expunge()
            
                else:
                    result = imap.uid('COPY', str(i), folder_error)
                    if result[0] == 'OK':
                        if delete==-1:
                            mov, data = imap.uid('STORE', str(i) , '+FLAGS', '(\Deleted)')
                        imap.expunge()


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
    
