import datetime as dt
import jwt
from core import log
from core.exceptions import  WrongJwtTokenType

logger=log.create_logger(__name__)

class JwtToken(object):
    def __init__(self, secret, algorithm, token_use):
        """
        token_use.........: access or refresh
        """
        super().__init__()
        self._secret = secret
        self._algorithm = algorithm
        self._token_use = token_use
        self._jwt_aud = "/api/core/login.py"
        self._jwt_iss = "CLIENT ID"
        self._raise_error = False

        self._token = ""
        self._payload = ""

    @property
    def raise_error(self):
        return self._raise_error

    @raise_error.setter
    def raise_error(self, value):
        self._raise_error = value

    @property
    def payload(self):
        return self._payload

    @property
    def token(self):
        return self._token

    def encode(self, username, session_id, expiry_minutes, **params):
        """
        expiry_minutes....: Validity period in minutes
        session_id........: restapi Session ID
        username..........: restapi Username
        """
        current_time = dt.datetime.now(dt.timezone.utc)
        expiry = round(current_time.timestamp() + expiry_minutes * 60)

        payload = {
            "sid": session_id,
			"iss": self._jwt_iss,
			"sub": username,
			"aud": self._jwt_aud,
			"exp": expiry,
            "token_use": self._token_use
		}

        try:
            token = jwt.encode(payload,self._secret,algorithm=self._algorithm)
        except jwt.InvalidKeyError as e:
            logger.error(f"Key to short for {self._algorithm}")
            if self._raise_error:
                raise
            else:
                return False

        self._token = token


    def decode(self, token):
        self._token = token
        decoded=""
        try:
            decoded = jwt.decode(token, self._secret,audience=self._jwt_aud, algorithms=[self._algorithm])
        except jwt.InvalidAudienceError:
            logger.error(f"Invalid Audience")
            if self._raise_error:
                raise
            else:
                return False
        except jwt.ExpiredSignatureError:
            logger.error(f"Session experied")
            if self._raise_error:
                raise
            else:
                return False
        finally:
            if type(decoded) is dict and 'token_use' in decoded:
                if decoded['token_use'] != self._token_use:
                    logger.error(f"Wrong token_use")
                    if self._raise_error:
                        raise WrongJwtTokenType(f"{decoded['token_use']}")
                    else:
                        return False

        self._payload = decoded
        return True


if __name__ == '__main__':
    jwt_token=JwtToken(secret="12345678901234567890123456789012345", algorithm="HS256", token_use="access")
    jwt_token.encode("root", "1234567890", 10)
    print(jwt_token.token)

    jwt_token2=JwtToken(secret="12345678901234567890123456789012345", algorithm="HS256", token_use="access")
    jwt_token2.decode(jwt_token.token)
    print(jwt_token2.payload)
