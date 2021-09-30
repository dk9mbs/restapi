#DROP TABLE IF EXISTS api_audit_log;
#DROP TABLE IF EXISTS api_event_handler;
#DROP TABLE IF EXISTS api_event_type;
#DROP TABLE IF EXISTS api_group_permission;
#DROP TABLE IF EXISTS api_user_group;
#DROP TABLE IF EXISTS api_session;
#DROP TABLE IF EXISTS api_dataview;
#DROP TABLE IF EXISTS api_table;
#DROP TABLE IF EXISTS api_user;
#DROP TABLE IF EXISTS api_group;
#DROP TABLE IF EXISTS api_solution;

#deprecated
#DROP TABLE IF EXISTS api_plugin_type;

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
    VALUES (7,'api_session', 'api_session','id','Int','Iser_id',-1);

INSERT IGNORE INTO api_table(id,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (8,'api_portal', 'api_portal','id','String','name',-1);

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



CREATE TABLE IF NOT EXISTS api_table_view(
    id int NOT NULL AUTO_INCREMENT,
    table_id int NOT NULL,
    fetch_xml text NOT NULL,
    col_definition text NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(table_id) REFERENCES api_table(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_table_view (id,table_id,fetch_xml, col_definition) VALUES (
1,1,'<restapi type="select">
<table name="dummy"/>
<filter type="and">
<condition field="name" value="$$query$$" operator=" like "/>
</filter>
</restapi>','[{"name": "id", "header":"#"},
{"name": "name", "header":"Name"},
{"name": "Port", "header":"TCP Port"}]');
