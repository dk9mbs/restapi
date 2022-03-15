import sys
import os
from flaskext.mysql import MySQL

from core.exceptions import RestApiNotAllowed, FileNotFoundInDatabase
from core import log
from core.meta import read_table_meta
from core.exceptions import TableMetaDataNotFound

logger=log.create_logger(__name__)

class File:
    def __init__(self):
        self._file_id=0

    def get_file_id(self):
        return self._file_id

    def read_file(self,context, remote_path):
        connection=context.get_connection()

        sql=f"""
        SELECT a.file, a.mime_type,a.name FROM api_file a
        WHERE a.path_hash=PASSWORD(%s);
        """
        logger.info(f"GET file {remote_path}")
        cursor=connection.cursor()
        cursor.execute(sql, [remote_path])
        result=cursor.fetchone()
        cursor.fetchall()
        cursor.close()

        return result


    def create_file(self, context, file, remote_path):
        connection=context.get_connection()

        file_bytes=file.read()
        mime_type="image/jpeg"
        size=len(file_bytes)
        file_name=file.filename
        full_path=os.path.join(remote_path, file_name)

        sql=f"""
        INSERT INTO api_file (name,file,size,mime_type,path,path_hash) VALUES (%s,%s,%s,%s,%s,PASSWORD(%s));
        """

        cursor=connection.cursor()
        cursor.execute(sql, [file.filename,file_bytes,size,mime_type,full_path,full_path])
        self._file_id=cursor.lastrowid
        cursor.fetchall()
        cursor.close()

    def update_file(self, context, file, remote_path):
        connection=context.get_connection()
        file_bytes=file.read()
        self.__file_id_by_path(context,connection,remote_path)

        sql=f"""
        UPDATE api_file SET file=%s WHERE path_hash=PASSWORD(%s)
        """

        cursor=connection.cursor()
        cursor.execute(sql, [file_bytes, remote_path])
        cursor.fetchall()
        cursor.close()


    def __file_id_by_path(self,context, connection,remote_path):

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


