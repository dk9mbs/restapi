class AuditLog:

    @staticmethod
    def log(context,type,record_id,table_name,field_name,old_value,value):
        if value==old_value:
            return

        sql=f"""
        INSERT INTO api_audit_log (type,record_id,table_name,field_name,old_value,value,modified_on,modified_by) 
            VALUES
            (%s,%s,%s,%s,%s,%s,now(),%s)
        """
        params=[type,record_id,table_name,field_name,old_value,value,context.get_user_id()]
        connection=context.get_connection()
        cursor=connection.cursor()
        cursor.execute(sql,params)

