import requests

class RestApiClient:
    def __init__(self):
        self.__session_id=None

    def login(self, username, password):
        headers={
            "username":username,
            "password":password
        }

        r=requests.post('http://localhost:5000/api/v1.0/core/login', headers=headers)

        if r.status_code==200:
            session=r.cookies['session']
        else:
            session=None

        #print("HTTP Status code => %s" % r.status_code)
        #print(r.text)

        # the one and only session you need
        cookies={"session": session}
        self.__session_id=session_id

    def logout(self):
        pass

print("*** login with username and password ***")
headers={
    "username":"guest",
    "password": "password"
}

r=requests.post('http://localhost:5000/api/v1.0/core/login', headers=headers)

if r.status_code==200:
    session=r.cookies['session']
else:
    session=None

print("HTTP Status code => %s" % r.status_code)
print(r.text)

# the one and only session you need
cookies={"session": session}

print("*** delete the record ***")
r=requests.delete('http://localhost:5000/api/v1.0/data/dummy/99', cookies=cookies)
print("HTTP Status code => %s" % r.status_code)
print(r.text)


print("*** addnew record ***")
data = {'id':99,'name':'IC735', 'port':3306}
headers={"Content-Type":"application/json"}
r=requests.post('http://localhost:5000/api/v1.0/data/dummy', headers=headers, json=data, cookies=cookies)
print("HTTP Status code => %s" % r.status_code)
print(r.text)


print("*** read the record ***")
r=requests.get('http://localhost:5000/api/v1.0/data/dummy/99', cookies=cookies)
print("HTTP Status code => %s" % r.status_code)
print(r.text)

print("*** update record ***")
data = {'id':99,'name':'GD77', 'port':3307}
headers={"Content-Type":"application/json"}
r=requests.put('http://localhost:5000/api/v1.0/data/dummy/99', headers=headers, json=data, cookies=cookies)
print("HTTP Status code => %s" % r.status_code)
print(r.text)

print("*** after the update read the record again ***")
r=requests.get('http://localhost:5000/api/v1.0/data/dummy/99', cookies=cookies)
print("HTTP Status code => %s" % r.status_code)
print(r.text)


print("*** logoff and remove session from server ***")
r=requests.post('http://localhost:5000/api/v1.0/core/logoff', cookies=cookies)
print("HTTP Status code => %s" % r.status_code)
print(r.text)
