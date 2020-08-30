import argparse
import sys
import json
from clientlib import RestApiClient



parser = argparse.ArgumentParser(description='Administrate the restapi.')
parser.add_argument('--apiusername','-u', type=str, help='Restapi username')
parser.add_argument('--apipassword','-p', type=str, help='Restapi password')
parser.add_argument('--url','-U', type=str, help='http://localhost:5000/api')
parser.add_argument('--command', '-c', type=str, help='Main command')
parser.add_argument('--username', type=str, help='User you want to change')
parser.add_argument('--query', '-q', type=str, help='Search string for listqueries')
args = parser.parse_args()

url=args.url
apiusername=args.apiusername
apipassword=args.apipassword
command=args.command

if url==None:
    url="http://localhost:5000/api"

rest=RestApiClient(url)
rest.login(apiusername, apipassword)


def format_headline(json):
    hl=[]
    l=[]
    for field in json:
        if 'ljust' in field:
            hl.append("|"+str(field['description']).ljust(int(field['ljust'])))
            l.append("+"+"".ljust(int(field['ljust']),"-" )  )
        else:
            hl.append("|"+str(field['description']).rjust(int(field['rjust'])))
            l.append("+"+"".rjust(int(field['rjust']),"-" )  )


    headline=''.join(hl)+"|"
    line=''.join(l)+"+"

    return (headline, line)

def format_dataline(data, json):
    tmp=[]
    for field in json:
        if 'ljust' in field:
            tmp.append("|"+str(data[field['field']]).ljust(int(field['ljust'])))
        else:
            tmp.append("|"+str(data[field['field']]).rjust(int(field['rjust'])))

    return ''.join(tmp)+"|"


def username_to_id(rest,username):
    fetch=f"""
        <restapi>
            <table name="api_user"/>
            <filter type="and">
                <condition field="username" value="{username}" operator="="/>
            </filter>
        </restapi>
    """
    users=json.loads(rest.read_multible("api_user",fetch))
    if users==[]:
        raise NameError('Username not found')

    if len(users)>1:
        raise NameError('Username not unique!')

    return users[0]['id']

def list_groups(rest, query):
    if query==None:
        query=""

    fetch=f"""
    <restapi>
        <table name="api_group"/>
        <filter type="AND">
        <condition field="groupname" value="{query}%" operator="like"/>
        </filter>
    </restapi>
    """

    groups=json.loads(rest.read_multible("api_group", fetch))
    fields=[
        {"description":"ID","field":"id","rjust":"10"},
        {"description":"Groupname","field":"groupname","ljust":"25"},
    ]

    headline, line=format_headline(fields)

    print(line)
    print(headline)
    print(line)

    for group in groups:
        print(format_dataline(group, fields))

    print(line)

def list_users(rest, query):

    if query==None:
        query=""

    fetch=f"""
    <restapi>
        <table name="api_user"/>
        <filter type="AND">
        <condition field="username" value="{query}%" operator="like"/>
        </filter>
    </restapi>
    """
    users=json.loads(rest.read_multible("api_user", fetch))
    print(users)
    fields=[
        {"description":"ID","field":"id","rjust":"10"},
        {"description":"Username","field":"username","ljust":"25"},
        {"description":"Disabled","field":"disabled","ljust":"10"},
        {"description":"Admin","field":"is_admin","ljust":"10"},
    ]

    headline, line=format_headline(fields)

    print(line)
    print(headline)
    print(line)

    for user in users:
        print(format_dataline(user, fields))

    print(line)


def set_user_status(rest, username, disabled):
    user_id=username_to_id(rest, username)
    if disabled==False:
        status=0
    else:
        status=-1

    print(rest.update("api_user", user_id, {"disabled":status}))

if command=='listusers':
    list_users(rest, args.query)
elif command=='listgroups':
    list_groups(rest, args.query)
elif command == 'test':
    username_to_id(rest, args.username)
elif command == 'disuser':
    set_user_status(rest, args.username, True)
elif command == 'enuser':
    set_user_status(rest, args.username, False)

rest.logoff()
