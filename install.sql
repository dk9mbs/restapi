DROP TABLE IF EXISTS api_group_permission;
DROP TABLE IF EXISTS api_user_group;
DROP TABLE IF EXISTS api_session;
DROP TABLE IF EXISTS api_dataview;
DROP TABLE IF EXISTS api_table;
DROP TABLE IF EXISTS api_user;
DROP TABLE IF EXISTS api_group;

CREATE TABLE IF NOT EXISTS api_table (
    id int NOT NULL AUTO_INCREMENT,
    alias varchar(250) NOT NULL,
    table_name varchar(250) NOT NULL,
    id_field_name varchar(250) NOT NULL,
    id_field_type varchar(50) NOT NULL COMMENT 'String,Int',
    desc_field_name varchar(250) NOT NULL COMMENT 'Name of the description field',
    view_sql text NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(alias),
    UNIQUE KEY(table_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO api_table (id,alias,table_name,id_field_name,id_field_type,desc_field_name)
    VALUES (1,'dummy','dummy','id','Int','name');


CREATE TABLE IF NOT EXISTS api_user (
    id int NOT NULL AUTO_INCREMENT,
    username varchar(100) NOT NULL,
    password varchar(100) NOT NULL,
    disabled smallint NOT NULL DEFAULT '0',
    is_admin smallint NOT NULL DEFAULT '0',
    PRIMARY KEY(id),
    UNIQUE KEY(username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO api_user (id,username,password,disabled,is_admin) VALUES (1,'root','password',0,-1);
INSERT INTO api_user (id,username,password,disabled,is_admin) VALUES (99,'system','password',-1,-1);
INSERT INTO api_user (id,username,password) VALUES (100,'guest','password');

CREATE TABLE IF NOT EXISTS api_group (
    id int NOT NULL AUTO_INCREMENT,
    groupname varchar(100) NOT NULL,
    is_admin smallint NOT NULL DEFAULT '0',
    PRIMARY KEY(id),
    UNIQUE KEY(groupname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO api_group (id,groupname,is_admin) VALUES (1,'sysadmin',-1);
INSERT INTO api_group (id,groupname,is_admin) VALUES (100,'guest',0);

CREATE TABLE IF NOT EXISTS api_user_group (
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    group_id int NOT NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(user_id,group_id),
    FOREIGN KEY(user_id) REFERENCES api_user(id),
    FOREIGN KEY(group_id) REFERENCES api_group(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO api_user_group (user_id,group_id) VALUES (100,100);

CREATE TABLE IF NOT EXISTS api_group_permission(
    id int NOT NULL AUTO_INCREMENT,
    group_id int NOT NULL,
    table_id int NOT NULL,
    mode_create smallint NOT NULL DEFAULT '0',
    mode_read smallint NOT NULL DEFAULT '0',
    mode_update smallint NOT NULL DEFAULT '0',
    mode_delete smallint NOT NULL DEFAULT '0',
    PRIMARY KEY(id),
    UNIQUE KEY(group_id, table_id),
    FOREIGN KEY(group_id) REFERENCES api_group(id),
    FOREIGN KEY(table_id) REFERENCES api_table(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO api_group_permission (group_id,table_id, mode_read) VALUES (100,1,-1);

CREATE TABLE IF NOT EXISTS api_session (
    id varchar(100) NOT NULL,
    user_id int NOT NULL,
    session_values text NOT NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    last_access_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES api_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




