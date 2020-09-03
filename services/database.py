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
        # i case of no permission check_permission raise an errror
        if not run_as_system:
            command_builder.check_permission(context)

        #
        # read all plugins
        #
        main_table=command_builder.get_main_table()
        #
        # execute before plugins
        #
        paras=command_builder.get_sql_parameter()
        sql=command_builder.get_sql()
        print(sql)
        print(paras)
        cursor=context.get_connection().cursor()
        cursor.execute(sql, paras)
        #
        # execute all after plugins
        #
        if command_builder.get_auto_commit()==1:
            context.get_connection().commit()

        rs=Recordset(cursor)
        if fetch_mode != -1:
            rs.read(fetch_mode)

        return rs



