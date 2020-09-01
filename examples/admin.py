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
parser.add_argument('--password', type=str, help='Password for given --username')
parser.add_argument('--groupname', type=str, help='For add or remove --username to group or list permissions')
parser.add_argument('--tablename', type=str, help='Tablename')
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

def groupname_to_id(rest,groupname):
    fetch=f"""
        <restapi>
            <table name="api_group"/>
            <filter type="and">
                <condition field="groupname" value="{groupname}" operator="="/>
            </filter>
        </restapi>
    """
    groups=json.loads(rest.read_multible("api_group",fetch))
    if groups==[]:
        raise NameError('Groupname not found')

    if len(groups)>1:
        raise NameError('Groupname not unique!')

    return groups[0]['id']


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

def add_user(rest, username, password):
    if username==None:
        raise NameError('you must enter a valid username (--username)')

    if password==None:
        raise NameError('You must enter a password for the new user (--password)')

    data={"username":username, "disabled":-1, "password":"password"}
    print(rest.add("api_user", data))

def change_password(rest, username, password):
    if username==None:
        raise NameError('you must enter a valid username (--username)')

    if password==None:
        raise NameError('You must enter a password for the new user (--password)')

    user_id=username_to_id(rest, username)
    data={"password":password}
    print(rest.update("api_user",user_id, data))

def add_user_to_group(rest, username, groupname):
    if username==None:
        raise NameError('you must enter a valid username (--username)')

    if groupname==None:
        raise NameError('You must enter a password for the new user (--password)')

    user_id=username_to_id(rest, username)
    group_id=groupname_to_id(rest, groupname)

    data={"user_id":user_id, "group_id":group_id}

    print(rest.add("api_user_group", data))

def remove_user_to_group(rest, username, groupname):
    if username==None:
        raise NameError('you must enter a valid username (--username)')

    if groupname==None:
        raise NameError('You must enter a password for the new user (--password)')

    user_id=username_to_id(rest, username)
    group_id=groupname_to_id(rest, groupname)

    fetch=f"""
    <restapi>
        <table name="api_user_group"/>
        <filter type="and">
            <condition field="group_id" value="{group_id}" operator="="/>
            <condition field="user_id" value="{user_id}" operator="="/>
        </filter>
    </restapi>
    """
    usergroup=json.loads(rest.read_multible("api_user_group", fetch))
    if usergroup==[]:
        raise NameError('User not in group')

    id=usergroup[0]['id']
    print(rest.delete("api_user_group", id))

def list_permissions(rest, username, groupname, tablename):
    if username==None:
        username=""
    if groupname==None:
        groupname=""
    if tablename==None:
        tablename=""

    fetch=f"""
    <restapi>
        <table name="api_group_permission" alias="p"/>
        <joins>
            <join type="inner" table="api_group" alias="g" condition="p.group_id=g.id"/>
            <join type="inner" table="api_table" alias="t" condition="p.table_id=t.id"/>
            <join type="inner" table="api_user_group" alias="ug" condition="ug.group_id=g.id"/>
            <join type="inner" table="api_user" alias="u" condition="u.id=ug.user_id"/>
        </joins>
        <select>
            <field name="username" table_alias="u"/>
            <field name="groupname" table_alias="g"/>
            <field name="table_name" table_alias="t"/>
            <field name="mode_create" table_alias="p"/>
            <field name="mode_read" table_alias="p"/>
            <field name="mode_update" table_alias="p"/>
            <field name="mode_delete" table_alias="p"/>
        </select>
        <filter type="and">
            <condition field="username" alias="u" value="{username}%" operator="like"/>
            <condition field="groupname" alias="g" value="{groupname}%" operator="like"/>
            <condition field="table_name" alias="t" value="{tablename}%" operator="like"/>
            <condition field="disabled" alias="u" value="0" operator="="/>
        </filter>
        <orderby>
            <field name="username" alias="u" sort="ASC"/>
            <field name="groupname" alias="g" sort="ASC"/>
            <field name="table_name" alias="t" sort="ASC"/>
        </orderby>
    </restapi>
    """
    permissions=json.loads(rest.read_multible("api_group_permissions", fetch))
    fields=[
        {"description":"User","field":"username","ljust":"25"},
        {"description":"Groupname","field":"groupname","ljust":"25"},
        {"description":"Table","field":"table_name","ljust":"25"},
        {"description":"Create","field":"mode_create","rjust":"6"},
        {"description":"Read","field":"mode_read","rjust":"6"},
        {"description":"Update","field":"mode_update","rjust":"6"},
        {"description":"Delete","field":"mode_delete","rjust":"6"},
    ]

    headline, line=format_headline(fields)

    print (line)
    print (headline)
    print (line)
    for permission in permissions:
        print(format_dataline(permission, fields))

    print(line)

def list_sessions(rest):
    fetch=f"""
    <restapi>
        <table name="api_session"/>
        <orderby>
            <field name="last_access_on" sort="ASC"/>
        </orderby>
    </restapi>
    """
    sessions=json.loads(rest.read_multible("api_session", fetch))
    fields=[
        {"description":"SessionID","field":"id","ljust":"25"},
        {"description":"UserID","field":"user_id","ljust":"10"},
        {"description":"Created on","field":"created_on","ljust":"25"},
        {"description":"Last Access","field":"last_access_on","ljust":"25"},
    ]

    headline, line=format_headline(fields)
    print(line)
    print(headline)
    print(line)

    #for session in sessions:
    #    print(format_dataline(session, fields))

    print(line)



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
elif command == 'adduser':
    add_user(rest, args.username, args.password)
elif command == 'chpasswd':
    change_password(rest, args.username, args.password)
elif command == 'addtogroup':
    add_user_to_group(rest, args.username, args.groupname)
elif command == 'rmfromgroup':
    remove_user_to_group(rest, args.username, args.groupname)
elif command == 'permissions':
    list_permissions(rest, args.username, args.groupname, args.tablename)
elif command == 'listsessions':
    list_sessions(rest)
else:
    print("use -h switch")

rest.logoff()
