
class Permission:
    def __init__(self):
        pass

    def validate(self,context,mode,username,table):
        sql="""
        SELECT * FROM api_user WHERE username=%s AND disabled=%s AND is_admin=%s
        """

        if mode.lower()=="insert": mode="create"
        if mode.lower()=="select": mode="read"

        connection=context.get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,[username,0,-1])
        systemuser=cursor.fetchone()
        cursor.fetchall()
        if not systemuser==None:
            return True

        sql=f"""
        SELECT p.mode_read,p.mode_create,p.mode_update,p.mode_delete,u.is_admin,p.table_id 
            FROM api_user u
            INNER JOIN api_user_group ug ON ug.user_id=u.id
            INNER JOIN api_group_permission p ON p.group_id=ug.group_id
            INNER JOIN api_table t ON t.id=p.table_id
            WHERE (t.table_name=%s OR t.alias=%s) AND u.username=%s AND mode_{mode}=%s
        """

        cursor=connection.cursor()
        cursor.execute(sql, [table, table, username, -1])
        permission=cursor.fetchone()
        cursor.fetchall()


        if permission==None:
            self._add_log(connection, 'ERROR', table, table, username, mode)
            return False

        #self._add_log(connection, 'SUCCESS', table, table, username, mode)
        return True


    def _add_log(self,connection, log_type, table_name, table_alias, username, mode):
        sql=f"""INSERT INTO api_permission_log (log_type, table_name,table_alias, username, mode) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor=connection.cursor()
        cursor.execute(sql, [log_type, table_name, table_alias, username, mode])
        cursor.fetchall()
        cursor.close()