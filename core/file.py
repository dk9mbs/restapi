import sys
import os
import pathlib
from flaskext.mysql import MySQL
import mimetypes

from core.exceptions import RestApiNotAllowed, FileNotFoundInDatabase, UnknownMimeType
from core import log
from core.meta import read_table_meta
from core.exceptions import TableMetaDataNotFound
from core.setting import Setting
from core.meta import read_table_meta
from core.user_group_tools import UserGroupTools

logger=log.create_logger(__name__)

class File:
    def __init__(self):
        self._file_id=0

    def get_file_id(self):
        return self._file_id

    def read_file(self,context, remote_path):
        connection=context.get_connection()
        where=""

        meta=read_table_meta(context, alias="api_file")
        if meta['enable_record_permission']!=0:
            where=f"AND api_fn_rec_permission('"+context.get_username()+"','"+"api_file"+"',a.id, 'SELECT') "

        sql=f"""
        SELECT a.file, a.mime_type,a.name,a.text,a.mode FROM api_file a
        WHERE a.path_hash=PASSWORD(%s) {where};
        """
        logger.info(f"GET file {remote_path} {sql}")
        cursor=connection.cursor()
        cursor.execute(sql, [remote_path])
        result=cursor.fetchone()
        cursor.fetchall()
        cursor.close()

        return result


    def create_file(self, context, file, remote_path, **args):
        connection=context.get_connection()

        file_bytes=file.read()
        size=len(file_bytes)
        file_name=file.filename

        extension=pathlib.Path(file_name).suffix.lower()

        if Setting.get_value(context, "core.debug.level")=='0':
            logger.info(f"Filename: {file_name}")
            logger.info(f"Extension: {extension}")

        if not f"{extension}" in mimetypes.types_map:
            if extension==".p7s":
                mime_type="application/pkcs7-signature"
            elif extension==".sig" or extension==".asc" or file_name=="OpenPGP_signature":
                mime_type="application/pgp-signature"
            else:
                raise UnknownMimeType(f"Extension: {extension}")
        else:
            mime_type=mimetypes.types_map[extension]

        full_path=os.path.join(remote_path, file_name)

        sql=f"""
        INSERT INTO api_file (name,file,size,mime_type,path,path_hash) VALUES (%s,%s,%s,%s,%s,PASSWORD(%s));
        """

        cursor=connection.cursor()
        cursor.execute(sql, [file.filename,file_bytes,size,mime_type,full_path,full_path])
        self._file_id=cursor.lastrowid
        cursor.fetchall()

        # only in case of activate record permission add anew one
        meta=read_table_meta(context,alias='api_file')
        if meta['enable_record_permission']!=0:
            UserGroupTools.add_record_permission(context, meta['id'], context.get_userinfo()['user_id'] , 
                self._file_id)

        # create the reference
        if "reference_field_name" in args:
            reference_field_name=args['reference_field_name']
            reference_id=args['reference_id']
            sql=f"""
            update api_file SET {reference_field_name}=%s WHERE id=%s;
            """
            cursor.execute(sql, [reference_id, self._file_id])
            cursor.fetchall()

        cursor.close()

    def exists_file(self, context, remote_path):
        try:
            self._file_id_by_path(context,context.get_connection() , remote_path)
            return True
        except:
            return False

    def update_file(self, context, file, remote_path, **args):
        connection=context.get_connection()
        file_bytes=file.read()
        self._file_id_by_path(context,connection,remote_path)

        sql=f"""
        UPDATE api_file SET file=%s WHERE path_hash=PASSWORD(%s)
        """

        cursor=connection.cursor()
        cursor.execute(sql, [file_bytes, remote_path])
        cursor.fetchall()
        cursor.close()


    def _file_id_by_path(self,context, connection,remote_path):

        sql=f"""
        SELECT a.id FROM api_file a
        WHERE a.path_hash=PASSWORD(%s);
        """

        cursor=connection.cursor()
        cursor.execute(sql, [remote_path])
        result=cursor.fetchone()
        cursor.fetchall()
        cursor.close()
        if result==None:
            raise FileNotFoundInDatabase(f"Filename: {remote_path}")

        self._file_id=result['id']


