

class Context:
    def __init__(self):
        self.__session_id=None
        self.__connection=None
        self.__userinfo=None
        self.__session_values=None
        self._auto_logoff=False

    def __del__(self):
        pass

    def get_username(self):
        if self.__userinfo==None:
            raise NameError('there is no userinfo object in this context!')
        if not 'username' in self.__userinfo:
            raise NameError('missing attribute username in userinfo in this context')

        return self.__userinfo['username']

    def get_auto_logoff(self):
        return self._auto_logoff

    def set_auto_logoff(self, value):
        self._auto_logoff=value

    def get_connection(self, database_id=0):
        return self.__connection

    def get_userinfo(self):
        return self.__userinfo

    def get_session_values(self):
        return self.__session_values

    def get_session_id(self):
        return self.__session_id

    def set_connection(self, connection, database_id=0):
        self.__connection=connection

    def set_userinfo(self, userinfo):
        self.__userinfo=userinfo

    def set_session_values(self, session_values):
        self.__session_values=session_values

    def set_session_id(self, session_id):
        self.__session_id=session_id

    """
    Close the context for the moement and commit or rollback the db changes.
    """
    def close(self, rollback=False):
        if not self.__connection==None:
            if rollback==True:
                self.__connection.rollback()
            else:
                self.__connection.commit()
            self.__connection.close()

