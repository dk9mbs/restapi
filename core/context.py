

class Context:
    def __init__(self):
        self.__session_id=None
        self.__connection=None
        self.__userinfo=None
        self.__session_values=None
        self._auto_logoff=False
        self.__args={}
        self.__userdata={}

    def __del__(self):
        pass

    def set_userdata(self, key, data):
        self.__userdata[key]=data

    def get_userdata(self, key, default=None):
        if not key in self.__userdata:
            return default

        return self.__userdata[key]


    def set_arg(self, name, value):
        self.__args[name]=value

    def get_arg(self, name, default=""):
        if name in self.__args:
            return self.__args[name]
        else:
            return default

    def get_args(self):
        return self.__args

    def get_username(self):
        if self.__userinfo==None:
            raise NameError('there is no userinfo object in this context!')
        if not 'username' in self.__userinfo:
            raise NameError('missing attribute username in userinfo in this context')

        return self.__userinfo['username']

    def get_user_id(self):
        if self.__userinfo==None:
            raise NameError('there is no userinfo object in this context!')
        if not 'user_id' in self.__userinfo:
            raise NameError('missing attribute user_id in userinfo in this context')

        return self.__userinfo['user_id']

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

    def get_session_value(self, name, default=None):
        if name in self.__session_values:
            return self.__session_values[name]

        return default

    def set_session_value(self, name, value):
        self.__session_values[name]=value

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

