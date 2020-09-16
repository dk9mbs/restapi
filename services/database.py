from flaskext.mysql import MySQL
import pymysql.cursors

from config import CONFIG
from core.database import Recordset
from core import log
from core.plugin import Plugin
from core.permission import Permission
from core import log
from core.fetchxmlparser import FetchXmlParser
from core.meta import read_table_meta

logger=log.create_logger(__name__)

class DatabaseServices:
    @staticmethod
    def exec(command_builder, context, run_as_system=False, fetch_mode=-1):
        #
        # Validate the permission
        # in case of no permission the check_permission function triggers an errror
        #

        if not run_as_system:
            for table in command_builder.get_tables():
                if not Permission().validate(context, command_builder.get_sql_type(), context.get_username(), table):
                    raise NameError (f"no permission ({command_builder.get_sql_type()}) for {context.get_username()} on {table}")

        if command_builder.get_sql_type().upper()=='UPDATE':
            sql, paras=command_builder.get_select()
            cursor=context.get_connection().cursor()
            cursor.execute(sql, paras)
            rsold=Recordset(cursor)
            rsold.read(0)
            logger.info(rsold.get_result())
            if len(rsold.get_result())>0:
                rec=rsold.get_result()[0]
                for k,v in rec.items():
                    if k in command_builder.get_sql_fields():
                        command_builder.get_sql_fields()[k]['old_value']=v
                logger.info(command_builder.get_sql_fields())

        params={"data": command_builder.get_sql_fields()}
        handler=Plugin(context, command_builder.get_main_table(),command_builder.get_sql_type())
        handler.execute('before', params)

        sql, paras =command_builder.get_sql()

        logger.info(sql)
        logger.info(paras)

        cursor=context.get_connection().cursor()
        cursor.execute(sql, paras)


        handler.execute('after', params)

        if command_builder.get_auto_commit()==1 or command_builder.get_auto_commit()==True:
            context.get_connection().commit()

        rs=Recordset(cursor)
        if fetch_mode != -1:
            rs.read(fetch_mode)

        return rs



