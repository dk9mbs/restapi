from flaskext.mysql import MySQL
from core.fetchxmlparser import FetchXmlParser
import pymysql.cursors
from config import CONFIG
from core.database import Recordset
from core import log
from core.plugin import Plugin

class DatabaseServices:
    @staticmethod
    def exec(command_builder, context, run_as_system=False, fetch_mode=-1):
        #
        # Validate the permission
        # in case of no permission the check_permission function triggers an errror
        #
        if not run_as_system:
            command_builder.check_permission(context)

        params={}
        handler=Plugin(context, command_builder.get_main_table(),command_builder.get_sql_type())
        handler.execute('before', params)

        paras=command_builder.get_sql_parameter()
        sql=command_builder.get_sql()

        log.create_logger(__name__).info(sql)
        log.create_logger(__name__).info(paras)

        cursor=context.get_connection().cursor()
        cursor.execute(sql, paras)


        handler.execute('after', params)

        if command_builder.get_auto_commit()==1:
            context.get_connection().commit()

        rs=Recordset(cursor)
        if fetch_mode != -1:
            rs.read(fetch_mode)

        return rs



