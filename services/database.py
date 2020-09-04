from flaskext.mysql import MySQL
from core.fetchxmlparser import FetchXmlParser
import pymysql.cursors
from config import CONFIG

from core.database import Recordset

class DatabaseServices:
    @staticmethod
    def exec(command_builder, context, run_as_system=False, fetch_mode=-1):
        #
        # Validate the permission
        # in case of no permission the check_permission function triggers an errror
        #
        if not run_as_system:
            command_builder.check_permission(context)

        paras=command_builder.get_sql_parameter()
        sql=command_builder.get_sql()
        print(sql)
        print(paras)
        cursor=context.get_connection().cursor()
        cursor.execute(sql, paras)

        if command_builder.get_auto_commit()==1:
            context.get_connection().commit()

        rs=Recordset(cursor)
        if fetch_mode != -1:
            rs.read(fetch_mode)

        return rs



