DELETE FROM api_table_view  WHERE solution_id=1;

CREATE TABLE IF NOT EXISTS api_solution(
    id int NOT NULL,
    name varchar(50)NOT NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_solution(id,name) VALUES (1,'restapi');

CREATE TABLE IF NOT EXISTS api_table (
    id int NOT NULL AUTO_INCREMENT,
    alias varchar(250) NOT NULL,
    table_name varchar(250) NOT NULL,
    id_field_name varchar(250) NOT NULL,
    id_field_type varchar(50) NOT NULL COMMENT 'String,Int',
    desc_field_name varchar(250) NOT NULL COMMENT 'Name of the description field',
    enable_audit_log smallint NOT NULL DEFAULT '0',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    UNIQUE KEY(alias),
    UNIQUE KEY(table_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_table (id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (1,'dummy','dummy','id','Int','name',-1);

INSERT IGNORE INTO api_table (id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (2,'api_user','api_user','id','Int','username',-1);

INSERT IGNORE INTO api_table (id,alias,table_name,id_field_name,id_field_type,desc_field_name, enable_audit_log)
    VALUES (3,'api_group','api_group','id','Int','groupname',-1);

INSERT IGNORE INTO api_table (id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (4,'api_user_group','api_user_group','id','Int','user_id',-1);

INSERT IGNORE INTO api_table (id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (5,'api_group_permission','api_group_permission','id','Int','group_id',-1);

INSERT IGNORE INTO api_table(id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (7,'api_session', 'api_session','id','Int','User_id',-1);

INSERT IGNORE INTO api_table(id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (8,'api_portal', 'api_portal','id','String','name',-1);

INSERT IGNORE INTO api_table(id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (9,'api_event_handler', 'api_event_handler','id','Int','table_name',0);

INSERT IGNORE INTO api_table(id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (10,'api_table', 'api_table','id','Int','table_name',0);

INSERT IGNORE INTO api_table(id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (11,'api_table_view_type', 'api_table_view_type','id','String','name',0);

INSERT IGNORE INTO api_table(id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (12,'api_table_view', 'api_table_view','id','String','name',0);

CREATE TABLE IF NOT EXISTS api_user (
    id int NOT NULL AUTO_INCREMENT,
    username varchar(100) NOT NULL,
    password varchar(100) NOT NULL,
    disabled smallint NOT NULL DEFAULT '0',
    is_admin smallint NOT NULL DEFAULT '0',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    UNIQUE KEY(username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_user (id,username,password,disabled,is_admin) VALUES (1,'root','password',0,-1);
INSERT IGNORE INTO api_user (id,username,password,disabled,is_admin) VALUES (99,'system','password',0,-1);
INSERT IGNORE INTO api_user (id,username,password) VALUES (100,'guest','password');

CREATE TABLE IF NOT EXISTS api_group (
    id int NOT NULL AUTO_INCREMENT,
    groupname varchar(100) NOT NULL,
    is_admin smallint NOT NULL DEFAULT '0',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    UNIQUE KEY(groupname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_group (id,groupname,is_admin) VALUES (1,'sysadmin',-1);
INSERT IGNORE INTO api_group (id,groupname,is_admin) VALUES (100,'guest',0);

CREATE TABLE IF NOT EXISTS api_user_group (
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    group_id int NOT NULL,
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    UNIQUE KEY(user_id,group_id),
    FOREIGN KEY(user_id) REFERENCES api_user(id),
    FOREIGN KEY(group_id) REFERENCES api_group(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_user_group (user_id,group_id) VALUES (100,100);

CREATE TABLE IF NOT EXISTS api_group_permission(
    id int NOT NULL AUTO_INCREMENT,
    group_id int NOT NULL,
    table_id int NOT NULL,
    mode_create smallint NOT NULL DEFAULT '0',
    mode_read smallint NOT NULL DEFAULT '0',
    mode_update smallint NOT NULL DEFAULT '0',
    mode_delete smallint NOT NULL DEFAULT '0',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    UNIQUE KEY(group_id, table_id),
    FOREIGN KEY(group_id) REFERENCES api_group(id),
    FOREIGN KEY(table_id) REFERENCES api_table(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_group_permission (group_id,table_id, mode_read) VALUES (100,1,-1);
INSERT IGNORE INTO api_group_permission (group_id,table_id, mode_read) VALUES (100,8,-1);

CREATE TABLE IF NOT EXISTS api_session (
    id varchar(100) NOT NULL,
    user_id int NOT NULL,
    session_values text NOT NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    last_access_on datetime NOT NULL DEFAULT current_timestamp,
    disabled smallint NOT NULL DEFAULT '0',
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES api_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS api_event_type(
    id varchar(50) NOT NULL,
    name varchar(50) NOT NULL,
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    UNIQUE KEY (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_event_type (id, name) VALUES ('before','On before');
INSERT IGNORE INTO api_event_type (id, name) VALUES ('after','On after');

CREATE TABLE IF NOT EXISTS api_event_handler (
    id int NOT NULL AUTO_INCREMENT,
    plugin_module_name varchar(500) NOT NULL COMMENT 'Namespace to the register function',
    publisher varchar(500) NOT NULL COMMENT 'Tablename or publisher of the event',
    event varchar(500) NOT NULL COMMENT 'name of trigger like insert or update',
    type varchar(50) NOT NULL,
    sorting int NOT NULL DEFAULT '100' COMMENT 'Sorting',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    FOREIGN KEY(type) REFERENCES api_event_type(id),
    INDEX (publisher, event),
    INDEX (publisher, event, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (1,'plugin_test','dummy','insert','before');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (2,'plugin_test','dummy','insert','after');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (3,'plugin_test','dummy','update','before');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (4,'plugin_test','dummy','update','after');




CREATE TABLE IF NOT EXISTS api_audit_log(
    id INT NOT NULL AUTO_INCREMENT,
    type varchar(50) NOT NULL,
    record_id varchar(250) NOT NULL,
    table_name varchar(250) NOT NULL,
    field_name varchar(250) NOT NULL,
    old_value text NULL,
    value text NULL,
    modified_on datetime NOT NULL,
    modified_by int NOT NULL,
    PRIMARY KEY(id),
    INDEX (table_name,record_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS api_portal(
    id varchar(50) NOT NULL,
    name varchar(100) NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_portal(id,name) VALUES ('default', 'default');
ALTER TABLE api_portal ADD COLUMN IF NOT EXISTS name varchar(100);

CREATE TABLE IF NOT EXISTS api_table_view_type(
    id varchar(10) NOT NULL,
    name varchar(50) NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_table_view_type(id,name,solution_id) VALUES('LISTVIEW','View for listviews',1);
INSERT IGNORE INTO api_table_view_type(id,name,solution_id) VALUES('SELECTVIEW','View for comboboxes',1);

CREATE TABLE IF NOT EXISTS api_table_view(
    id int NOT NULL AUTO_INCREMENT,
    name varchar(100) NOT NULL DEFAULT '<NEW>',
    type_id varchar(10) NOT NULL COMMENT 'LISTVIEW,SELECTVIEW,FORMVIEW',
    table_id int NOT NULL,
    id_field_name varchar(50) NOT NULL,
    fetch_xml text NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(table_id, type_id, name),
    FOREIGN KEY(table_id) REFERENCES api_table(id),
    FOREIGN KEY(solution_id) REFERENCES api_solution(id),
    FOREIGN KEY(type_id) REFERENCES api_table_view_type(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*
Views 
*/
INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
1,'LISTVIEW','default',1,'id',1,'<restapi type="select">
    <table name="dummy"/>
    <filter type="and">
        <condition field="name" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id"/>
        <field name="name"/>
        <field name="port"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
2,'SELECTVIEW','default',1,'id',1,'<restapi type="select">
    <table name="dummy"/>
    <select>
        <field name="id" alias="id"/>
        <field name="name" alias="name"/>
    </select>
</restapi>');


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
3,'LISTVIEW','default',7,'id',1,'<restapi type="select">
<table name="api_session" alias="s"/>
<filter type="and">
            <condition field="session_values" alias="s" value="$$query$$" operator=" like "/>
            <condition field="disabled" alias="s" value="0" operator=" like "/>
        </filter>
        <orderby>
            <field name="last_access_on" alias="s" sort="DESC"/>
        </orderby>
        <joins>
            <join type="inner" table="api_user" alias="u" condition="u.id=s.user_id"/>
        </joins>
        <select>
            <field name="id" table_alias="s"/>
            <field name="username" table_alias="u"/>
            <field name="created_on" table_alias="s"/>
            <field name="last_access_on" table_alias="s"/>
            <field name="disabled" table_alias="s"/>
        </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
4,'SELECTVIEW','default',7,'id',1,'<restapi type="select" top=50>
<table name="api_session" alias="s"/>
        <orderby>
            <field name="last_access_on" alias="s" sort="DESC"/>
        </orderby>
        <joins>
            <join type="inner" table="api_user" alias="u" condition="u.id=s.user_id"/>
        </joins>
        <select>
            <field name="id" table_alias="s"/>
            <field name="username" alias="name" table_alias="u"/>
        </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
5,'LISTVIEW','default',2,'id',1,'<restapi type="select">
    <table name="api_user" alias="u"/>
    <filter type="and">
        <condition field="username" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="u"/>
        <field name="username" table_alias="u" alias="name"/>
        <field name="disabled" table_alias="u"/>
        <field name="is_admin" table_alias="u"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
6,'SELECTVIEW','default',2,'id',1,'<restapi type="select">
    <table name="api_user" alias="u"/>
    <filter type="and">
        <condition field="username" value="%" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="u"/>
        <field name="username" table_alias="u" alias="name"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
7,'LISTVIEW','default',3,'id',1,'<restapi type="select">
    <table name="api_group" alias="g"/>
    <filter type="and">
        <condition field="groupname" table_alias="g" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="g"/>
        <field name="groupname" table_alias="g"/>
        <field name="is_admin" table_alias="g"/>
        <field name="solution_id" table_alias="g"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
8,'SELECTVIEW','default',3,'id',1,'<restapi type="select">
    <table name="api_group" alias="g"/>
    <filter type="and">
        <condition field="groupname" table_alias="g" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="g"/>
        <field name="groupname" table_alias="g" alias="name"/>
    </select>
</restapi>');


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
9,'LISTVIEW','default',4,'id',1,'<restapi type="select">
    <table name="api_user_group" alias="ug"/>
    <filter type="and">
        <condition field="groupname" value="$$query$$" operator=" like "/>
    </filter>
    <joins>
        <join type="inner" table="api_user" alias="u" condition="ug.user_id=u.id"/> 
        <join type="inner" table="api_group" alias="g" condition="ug.group_id=g.id"/> 
    </joins>
    <select>
        <field name="id" table_alias="ug"/>
        <field name="username" table_alias="u"/>
        <field name="groupname" table_alias="g"/>
        <field name="is_admin" table_alias="u" alias="Adminuser"/>
        <field name="is_admin" table_alias="g" alias="Admingroup"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
11,'LISTVIEW','default',9,'id',1,'<restapi type="select">
    <table name="api_event_handler" alias="eh"/>
    <filter type="or">
        <condition field="plugin_module_name" table_alias="eh" value="$$query$$" operator=" like "/>
        <condition field="publisher" table_alias="eh" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="eh"/>
        <field name="plugin_module_name" table_alias="eh"/>
        <field name="publisher" table_alias="eh"/>
        <field name="event" table_alias="eh"/>
        <field name="type" table_alias="eh"/>
        <field name="sorting" table_alias="eh"/>
        <field name="solution_id" table_alias="eh"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
12,'LISTVIEW','default',8,'id',1,'<restapi type="select">
    <table name="api_portal" alias="p"/>
    <filter type="or">
        <condition field="name" table_alias="p" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="p"/>
        <field name="name" table_alias="p"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
13,'SELECTVIEW','default',8,'id',1,'<restapi type="select">
    <table name="api_portal" alias="p"/>
    <filter type="or">
        <condition field="name" table_alias="p" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="p" alias="id"/>
        <field name="name" table_alias="p" alias="name"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
14,'LISTVIEW','default',5,'id',1,'<restapi type="select">
    <table name="api_group_permission" alias="gp"/>
    <filter type="or">
        <condition field="groupname" table_alias="g" value="$$query$$" operator=" like "/>
        <condition field="alias" table_alias="t" value="$$query$$" operator=" like "/>
        <condition field="table_name" table_alias="t" value="$$query$$" operator=" like "/>
    </filter>
    <joins>
        <join type="inner" table="api_group" alias="g" condition="gp.group_id=g.id"/>
        <join type="inner" table="api_table" alias="t" condition="gp.table_id=t.id"/>
    </joins>
    <select>
        <field name="id" table_alias="gp"/>
        <field name="alias" table_alias="t" alias="Tablename"/>
        <field name="groupname" table_alias="g" alias="Groupname"/>
        <field name="mode_read" table_alias="gp"/>
        <field name="mode_create" table_alias="gp"/>
        <field name="mode_update" table_alias="gp"/>
        <field name="mode_delete" table_alias="gp"/>
    </select>
</restapi>');


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
15,'LISTVIEW','default',10,'id',1,'<restapi type="select">
    <table name="api_table" alias="t"/>
    <filter type="or">
        <condition field="alias" table_alias="t" value="$$query$$" operator=" like "/>
        <condition field="table_name" table_alias="t" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="t"/>
        <field name="alias" table_alias="t"/>
        <field name="table_name" table_alias="t"/>
        <field name="desc_field_name" table_alias="t"/>
        <field name="id_field_name" table_alias="t"/>
        <field name="enable_audit_log" table_alias="t"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
16,'SELECTVIEW','default',10,'id',1,'<restapi type="select">
    <table name="api_table" alias="t"/>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="alias" table_alias="t" alias="name"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
17,'LISTVIEW','default',11,'id',1,'<restapi type="select">
    <table name="api_table_view_type" alias="t"/>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="name" table_alias="t" alias="name"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
18,'SELECTVIEW','default',11,'id',1,'<restapi type="select">
    <table name="api_table_view_type" alias="t"/>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="name" table_alias="t" alias="name"/>
    </select>
</restapi>');


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
21,'LISTVIEW','default',12,'id',1,'<restapi type="select">
    <table name="api_table_view" alias="tv"/>
        <filter type="or">
        <condition field="table_name" table_alias="t" value="$$query$$" operator=" like "/>
        <condition field="alias" table_alias="t" value="$$query$$" operator=" like "/>
    </filter>
    <joins>
        <join type="inner" table="api_table" alias="t" condition="tv.table_id=t.id"/>
    </joins>
    <select>
        <field name="id" table_alias="tv"/>
        <field name="name" table_alias="tv"/>
        <field name="type_id" table_alias="tv"/>
        <field name="table_name" table_alias="t"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
22,'SELECTVIEW','default',12,'id',1,'<restapi type="select">
    <table name="api_table_view" alias="tv"/>
        <filter type="or">
        <condition field="name" table_alias="tv" value="$$query$$" operator=" like "/>
    </filter>
    <joins>
        <join type="inner" table="api_table" alias="t" condition="tv.table_id=t.id"/>
    </joins>
    <select>
        <field name="id" table_alias="tv" alias="id"/>
        <field name="name" table_alias="tv" alias="name"/>
    </select>
</restapi>');