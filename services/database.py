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
from core.audit import AuditLog
from core.exceptions import RestApiNotAllowed

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
                    #raise NameError (f"no permission ({command_builder.get_sql_type()}) for {context.get_username()} on {table}")
                    raise RestApiNotAllowed (f"no permission ({command_builder.get_sql_type()}) for {context.get_username()} on {table}")

        logger.info(f"Try to read table metadata: {command_builder.get_main_table()}")
        meta=read_table_meta(context, table_name=command_builder.get_main_table())
        id_field_name=meta['id_field_name']
        id_field_type=meta['id_field_type']

        if command_builder.get_sql_type().upper()=='UPDATE':
            #meta=read_table_meta(context, table_name=command_builder.get_main_table())
            if meta['enable_audit_log']!=0:
                sql, paras=command_builder.get_select()
                cursor=context.get_connection().cursor()
                cursor.execute(sql, paras)
                rsold=Recordset(cursor)
                rsold.read(0)
                #id_field_name=meta['id_field_name']
                #id_field_type=meta['id_field_type']

                logger.info(rsold.get_result())
                if rsold.get_result()!=None:
                    for rec in rsold.get_result():
                        id=rec[id_field_name]
                        for k,v in rec.items():
                            if k in command_builder.get_sql_fields():
                                value=command_builder.get_sql_fields()[k]['value']
                                old_value=v
                                command_builder.get_sql_fields()[k]['old_value']=old_value
                                AuditLog.log(context,command_builder.get_sql_type(),id,command_builder.get_main_table(),k,old_value,value)

                        logger.info(command_builder.get_sql_fields())

        params={"data": command_builder.get_sql_fields()}
        handler=Plugin(context, command_builder.get_main_table(),command_builder.get_sql_type())
        handler.execute('before', params)

        sql, paras =command_builder.get_sql()

        logger.info(sql)
        logger.info(paras)

        tmp=sql
        for item in paras:
            tmp=tmp.replace("%s", f"'{item}'", 1)
        logger.info(tmp)

        cursor=context.get_connection().cursor()
        cursor.execute(sql, paras)

        handler.execute('after', params)

        if command_builder.get_auto_commit()==1 or command_builder.get_auto_commit()==True:
            context.get_connection().commit()

        rs=Recordset(cursor)
        if fetch_mode != -1:
            rs.read(fetch_mode)

        rs.get_columns()
        if command_builder.get_sql_type().upper() == "INSERT":
            if context.get_connection().insert_id()==0 or context.get_connection().insert_id()==None:
                rs.set_inserted_id(command_builder.get_sql_fields()[id_field_name]['value'])
            else:
                rs.set_inserted_id(context.get_connection().insert_id())
        return rs

    @staticmethod
    def recordset_to_list(context, rs, fields, reverse=False, default_value=0):
        result=dict()

        for field in fields:
            result[field]=[]

        for item in rs.get_result():
            for field in fields:
                result[field].append(item[field])

        for field in fields:
            if not field=="created_on" and not field=="chart_label":
                DatabaseServices.__fill_empty_list_items(result[field])


        if reverse==True:
            for field in fields:
                result[field].reverse()


        return result

    @staticmethod
    def __fill_empty_list_items(list, default=0):
        min=None;
        max=None;
        avg=0;

        for item in list:
            if min==None and not item==None:
                min=float(item)
            if max==None and not item==None:
                max=float(item)

            if not item==None and not min==None:
                if float(item)<float(min):
                    min=item

            if not item==None and not max==None:
                if float(item)>float(max):
                    max=item

        if min==None and max==None:
            avg=0
        else:
            avg=float((float(min)+float(max))/2)

        for i in range(len(list)):
            if list[i]==None:
                list[i]=avg

