CREATE TABLE IF NOT EXISTS dummy (
    id int NOT NULL auto_increment,
    name varchar(50) NOT NULL,
    Port int NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS api_solution(
    id int NOT NULL,
    name varchar(50)NOT NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_solution(id,name) VALUES (1,'restapi');
INSERT IGNORE INTO api_solution(id,name) VALUES (2,'customizing');


/* controls */
CREATE TABLE IF NOT EXISTS api_table_field_control(
    id int NOT NULL,
    name varchar(50) NOT NULL,
    control varchar(250) NOT NULL DEFAULT 'INPUT',
    control_config text NOT NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(name)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TRIGGER IF EXISTS api_table_field_control_before_insert;
delimiter //
create trigger api_table_field_control_before_insert before insert on api_table_field_control
for each row
begin
   if (NEW.control_config is null or NEW.control_config='' ) then
      set NEW.control_config = '{}';
   end if;
end
//
delimiter ;


INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (1,'Input','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (2,'Dropdown','SELECT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (3,'Date','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (4,'Time','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (5,'DateTime (do not use)','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (6,'Checkbox','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (7,'Button','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (8,'Color','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (9,'Datetime (local)','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (10,'Email','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (11,'Password','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (12,'URL','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (13,'Monat','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (14,'Number','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (16,'Telephone','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (17,'Week','INPUT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (18,'Multiline','TEXTAREA','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (19,'Yes No','BOOLEAN','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (100,'nicEdit','NIC-EDIT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (101,'ace Edit','ACE-EDIT','{}');

UPDATE api_table_field_control SET control_config='{"type": "text"}' WHERE id=1;
UPDATE api_table_field_control SET control_config='{}' WHERE id=2;
UPDATE api_table_field_control SET control_config='{"type": "date"}' WHERE id=3;
UPDATE api_table_field_control SET control_config='{"type": "time"}' WHERE id=4;
UPDATE api_table_field_control SET control_config='{"type": "datetime"}' WHERE id=5;
UPDATE api_table_field_control SET control_config='{"type": "checkbox"}' WHERE id=6;
UPDATE api_table_field_control SET control_config='{"type": "button"}' WHERE id=7;
UPDATE api_table_field_control SET control_config='{"type": "color"}' WHERE id=8;
UPDATE api_table_field_control SET control_config='{"type": "datetime-local"}' WHERE id=9;
UPDATE api_table_field_control SET control_config='{"type": "email"}' WHERE id=10;
UPDATE api_table_field_control SET control_config='{"type": "password"}' WHERE id=11;
UPDATE api_table_field_control SET control_config='{"type": "url"}' WHERE id=12;
UPDATE api_table_field_control SET control_config='{"type": "month"}' WHERE id=13;
UPDATE api_table_field_control SET control_config='{"type": "number"}' WHERE id=14;
UPDATE api_table_field_control SET control_config='{"type": "tel"}' WHERE id=16;
UPDATE api_table_field_control SET control_config='{"type": "week"}' WHERE id=17;
UPDATE api_table_field_control SET control_config='{}' WHERE id=18;
UPDATE api_table_field_control SET control_config='{"true_value": -1}' WHERE id=19;
UPDATE api_table_field_control SET control_config='{}' WHERE id=100;
UPDATE api_table_field_control SET control_config='{}' WHERE id=101;

CREATE TABLE IF NOT EXISTS api_table_field_type(
    id varchar(50) NOT NULL,
    name varchar(50) NOT NULL,
    control_id int NOT NULL DEFAULT '0' COMMENT 'Default control id for the ui',
    FOREIGN KEY (control_id) REFERENCES api_table_field_control(id),
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_table_field_type ADD COLUMN IF NOT EXISTS control_id int NOT NULL DEFAULT '1' COMMENT '';
ALTER TABLE api_table_field_type ADD CONSTRAINT FOREIGN KEY IF NOT EXISTS (control_id) REFERENCES api_table_field_control (id);


INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('default','Default',1) ON DUPLICATE KEY UPDATE control_id=1;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('string','String',1) ON DUPLICATE KEY UPDATE control_id=1;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('int','Int',14) ON DUPLICATE KEY UPDATE control_id=14;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('datetime','DateTime',9) ON DUPLICATE KEY UPDATE control_id=9;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('date','Date',3) ON DUPLICATE KEY UPDATE control_id=3;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('time','Time',4) ON DUPLICATE KEY UPDATE control_id=4;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('decimal','Decimal',14) ON DUPLICATE KEY UPDATE control_id=14;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('timestamp','Timestamp',9) ON DUPLICATE KEY UPDATE control_id=9;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('multiline','String (multiline)',100) ON DUPLICATE KEY UPDATE control_id=100;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('boolean','Boolean',6) ON DUPLICATE KEY UPDATE control_id=6;
INSERT IGNORE INTO api_table_field_type(id, name, control_id) VALUES ('lookup','Lookup',2) ON DUPLICATE KEY UPDATE control_id=2;


CREATE TABLE IF NOT EXISTS api_table (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(250) NOT NULL DEFAULT '',
    alias varchar(250) NOT NULL,
    table_name varchar(250) NOT NULL,
    id_field_name varchar(250) NOT NULL,
    id_field_type varchar(50) NOT NULL COMMENT 'String,Int',
    desc_field_name varchar(250) NOT NULL COMMENT 'Name of the description field',
    enable_audit_log smallint NOT NULL DEFAULT '0',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    FOREIGN KEY(id_field_type) REFERENCES api_table_field_type(id),
    PRIMARY KEY(id),
    UNIQUE KEY(alias),
    UNIQUE KEY(table_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_table ADD COLUMN IF NOT EXISTS name varchar(250) NOT NULL DEFAULT '' AFTER id;

INSERT IGNORE INTO api_table (id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (1,'Dummy','dummy','dummy','id','int','name',-1);

INSERT IGNORE INTO api_table (id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (2,'Benutzer','api_user','api_user','id','int','username',-1);

INSERT IGNORE INTO api_table (id,name,alias,table_name,id_field_name,id_field_type,desc_field_name, enable_audit_log)
    VALUES (3,'Gruppe','api_group','api_group','id','int','groupname',-1);

INSERT IGNORE INTO api_table (id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (4,'Benutzerzuordnung','api_user_group','api_user_group','id','int','user_id',-1);

INSERT IGNORE INTO api_table (id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (5,'Berechtigung','api_group_permission','api_group_permission','id','int','group_id',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (7,'Sitzung','api_session', 'api_session','id','int','id',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (8,'Portal','api_portal', 'api_portal','id','string','name',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (9,'Eventhandler','api_event_handler', 'api_event_handler','id','int','table_name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (10,'Tabelle','api_table', 'api_table','id','int','table_name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (11,'Ansichten Type','api_table_view_type', 'api_table_view_type','id','string','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (12,'Ansicht','api_table_view', 'api_table_view','id','string','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (13,'Feld','api_table_field', 'api_table_field','id','int','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (14,'Feldtyp','api_table_field_type', 'api_table_field_type','id','string','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (15,'App','api_ui_app', 'api_ui_app','id','int','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (16,'Navigations Itemtyp','api_ui_app_nav_item_type', 'api_ui_app_nav_item_type','id','int','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (17,'Navigations Item','api_ui_app_nav_item', 'api_ui_app_nav_item','id','int','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (18,'Inhaltstyp','api_portal_content_type', 'api_portal_content_type','id','int','name',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (19,'Inhalt','api_portal_content', 'api_portal_content','id','int','name',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (20,'Datei','api_file', 'api_file','id','int','name',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (21,'Einstellung','api_setting', 'api_setting','id','int','setting',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (22,'WWW Host','api_portal_host', 'api_portal_host','id','int','host',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (23,'Log','api_process_log', 'api_process_log','id','string','id',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (24,'Feld Element','api_table_field_control', 'api_table_field_control','id','int','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (25,'Lösung','api_solution', 'api_solution','id','int','name',0);


/* Bugfixing */
UPDATE api_table SET id_field_type='string' WHERE id_field_type='String';
UPDATE api_table SET id_field_type='int' WHERE id_field_type='Int';

UPDATE api_table set name=alias WHERE name IS NULL OR name='';

/* */

CREATE TABLE IF NOT EXISTS api_table_field(
    id int NOT NULL AUTO_INCREMENT,
    table_id int NOT NULL COMMENT 'ID from the sourcetable',
    label varchar(50) NOT NULL COMMENT 'Label/Columnheader for listviews and forms',
    name varchar(250) NOT NULL COMMENT 'Fieldname (source)',
    is_lookup smallint NOT NULL DEFAULT '0' COMMENT '0=No 1=YES',
    type_id varchar(50) NOT NULL COMMENT 'type of field',
    size int NOT NULL DEFAULT '0' COMMENT 'the size in case of string',
    allow_null smallint NOT NULL DEFAULT '0',
    default_value varchar(250) NULL,
    referenced_table_name varchar(250) NULL COMMENT 'referenced table name',
    referenced_table_id int NULL COMMENT 'api_table id',
    referenced_field_name varchar(250) NULL COMMENT 'Field from the referenced table',
    control_id int NULL COMMENT 'control_id',
    control_config text NOT NULL COMMENT 'Overwrite the type config',
    UNIQUE KEY(table_id, name),
    FOREIGN KEY(table_id) REFERENCES api_table(id),
    FOREIGN KEY(type_id) REFERENCES api_table_field_type(id),
    FOREIGN KEY(control_id) REFERENCES api_table_field_control(id),
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS referenced_table_id int NULL COMMENT 'api_table id' AFTER referenced_table_name;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS control_id int NULL COMMENT 'control_id';
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS control_config text NOT NULL COMMENT 'Overwrite the type config';
ALTER TABLE api_table_field ADD FOREIGN KEY(control_id) REFERENCES api_table_field_control(id);

UPDATE api_table_field SET control_config='{}' WHERE control_config='' or control_config IS NULL;

DROP TRIGGER IF EXISTS api_table_field_before_insert;
delimiter //
create trigger api_table_field_before_insert before insert on api_table_field
for each row
begin
   if (NEW.control_config is null or NEW.control_config='' ) then
      set NEW.control_config = '{}';
   end if;
end
//
delimiter ;

/* */

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
    publisher varchar(250) NOT NULL COMMENT 'Tablename or publisher of the event',
    event varchar(250) NOT NULL COMMENT 'name of trigger like insert or update',
    type varchar(50) NOT NULL,
    sorting int NOT NULL DEFAULT '100' COMMENT 'Sorting',
    solution_id int NOT NULL DEFAULT '1',
    run_async smallint NOT NULL DEFAULT '0' COMMENT '-1: run async 0=not async',
    config text NULL COMMENT 'locale event handler config',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    FOREIGN KEY(type) REFERENCES api_event_type(id),
    INDEX (publisher, event),
    INDEX (publisher, event, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS run_async smallint NOT NULL DEFAULT '0' COMMENT '-1: run async 0=not async' AFTER solution_id;

INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (1,'plugin_test','dummy','insert','before');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (2,'plugin_test','dummy','insert','after');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (3,'plugin_test','dummy','update','before');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (4,'plugin_test','dummy','update','after');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type,run_async) VALUES (5,'api_http_endpoint','dummy','insert','after',-1);
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type,run_async) VALUES (6,'api_http_endpoint','dummy','update','after',-1);
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type,run_async) VALUES (7,'api_clear_log','$timer_every_ten_minutes','execute','after',0);
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type,run_async) VALUES (8,'api_clear_session','$timer_every_hour','execute','after',0);

ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS run_async smallint NOT NULL default '0' COMMENT '-1: run async 0=not async';
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS config text NULL COMMENT 'locale event handler config';


CREATE TABLE IF NOT EXISTS api_process_log_status(
    id int NOT NULL,
    name varchar(100) NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_process_log_status(id,name) VALUES (0,'Pending');
INSERT IGNORE INTO api_process_log_status(id,name) VALUES (10,'Success');
INSERT IGNORE INTO api_process_log_status(id,name) VALUES (20,'Error');
INSERT IGNORE INTO api_process_log_status(id,name) VALUES (30,'Timeout');

DROP TABLE IF EXISTS api_process_log;

CREATE TABLE IF NOT EXISTS api_process_log (
    id varchar(36) NOT NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    status_id int NOT NULL DEFAULT '0'  COMMENT '0=pending 10=ok 20=Error 30=Timeout',
    error_text text NULL COMMENT 'in case of an exception',
    response_code int NULL COMMENT 'HTTP Code',
    request_msg text NULL COMMENT 'HTTP Request body',
    response_msg text NULL COMMENT '',
    response_on datetime NULL COMMENT 'Response on',
    config text NULL COMMENT 'Locale config from api_event_handler',
    event_handler_id int NOT NULL COMMENT 'Event handler id',
    run_async smallint NOT NULL DEFAULT '0',
    retries int NOT NULL default '0' COMMENT 'Number of retries in case of async processes',
    last_retry_on datetime NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(status_id) REFERENCES api_process_log_status(id),
    FOREIGN KEY(event_handler_id) REFERENCES api_event_handler(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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

/* portal */

CREATE TABLE IF NOT EXISTS api_portal(
    id varchar(50) NOT NULL,
    name varchar(100) NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_portal ADD COLUMN IF NOT EXISTS name varchar(100);
ALTER TABLE api_portal ADD COLUMN IF NOT EXISTS solution_id int NOT NULL;
ALTER TABLE api_portal ADD COLUMN IF NOT EXISTS template text NULL;

INSERT IGNORE INTO api_portal(id,name,solution_id) VALUES ('default', 'default',1);
UPDATE api_portal SET template='<!DOCTYPE HTML5>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="language" content="deutsch, de" />
<meta name="robots" content="index, follow" />
<meta name="author" content="dk9mbs.de" />
<meta http-equiv="expires" content="5" />
<meta name="Keywords" content="" >
<meta name="Description" content="" >
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Demo Portal</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

</head>
<body>
    <div id="content">
    {{ content }}
    </div>
</body>
</html>' WHERE id='default' AND template IS NULL;

CREATE TABLE IF NOT EXISTS api_portal_host(
    id int NOT NULL AUTO_INCREMENT,
    host varchar(250) NOT NULL,
    portal_id varchar(50) NOT NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(host),
    FOREIGN KEY(portal_id) REFERENCES api_portal(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_portal_host(host,portal_id) VALUES ('subdomain.domain.org','default');

CREATE TABLE IF NOT EXISTS api_portal_content_type(
    id int NOT NULL,
    name varchar(50) NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id),
    created_on datetime NOT NULL DEFAULT current_timestamp,
    FOREIGN KEY(solution_id) REFERENCES api_solution(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_portal_content_type(id,name,solution_id) VALUES (1, 'main',1);

CREATE TABLE IF NOT EXISTS api_portal_content(
    id int NOT NULL AUTO_INCREMENT,
    portal_id varchar(100) NOT NULL,
    name varchar(50) NOT NULL,
    type_id int NOT NULL,
    content text NULL COMMENT 'Please fill here your page content',
    solution_id int NOT NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    FOREIGN KEY(solution_id) REFERENCES api_solution(id),
    FOREIGN KEY(type_id) REFERENCES api_portal_content_type(id),
    FOREIGN KEY(portal_id) REFERENCES api_portal(id),
    UNIQUE KEY(name,portal_id,type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_portal_content AUTO_INCREMENT=1000000;

/* end portal */


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
App Management
 */
CREATE TABLE IF NOT EXISTS api_ui_app(
    id int NOT NULL AUTO_INCREMENT,
    name varchar(50) NOT NULL,
    description text NULL,
    home_url varchar(1000) NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(name),
    FOREIGN KEY(solution_id) REFERENCES api_solution(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE api_ui_app AUTO_INCREMENT=1000000;

INSERT IGNORE INTO api_ui_app (id, name,description,home_url,solution_id)
VALUES (
1,'Default','System Verwaltungs App','/ui/v1.0/data/view/api_user/default?app_id=1',1);

CREATE TABLE IF NOT EXISTS api_ui_app_nav_item_type(
    id int NOT NULL AUTO_INCREMENT,
    name varchar(50) NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (solution_id) REFERENCES api_solution(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE api_ui_app_nav_item_type AUTO_INCREMENT=1000000;

INSERT IGNORE INTO api_ui_app_nav_item_type (id,solution_id, name) VALUES (1,1, 'Sidebar');
INSERT IGNORE INTO api_ui_app_nav_item_type (id,solution_id, name) VALUES (2,1, 'Navbar');


CREATE TABLE IF NOT EXISTS api_ui_app_nav_item(
    id int NOT NULL,
    name varchar(50) NOT NULL,
    url varchar(1000) NOT NULL COMMENT 'Only the URL without querystring',
    query_string varchar(1000) NULL COMMENT 'Here only query_string args',
    app_id int NOT NULL,
    type_id int NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (app_id) REFERENCES api_ui_app(id),
    FOREIGN KEY (type_id) REFERENCES api_ui_app_nav_item_type(id),
    FOREIGN KEY (solution_id) REFERENCES api_solution(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_ui_app_nav_item AUTO_INCREMENT=1000000;

DELETE FROM api_ui_app_nav_item WHERE solution_id=1;

INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (1,1,'User','/ui/v1.0/data/view/api_user/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (2,1,'Tables','/ui/v1.0/data/view/api_table/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (3,1,'Sessions','/ui/v1.0/data/view/api_session/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (4,1,'Portals','/ui/v1.0/data/view/api_portal/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (5,1,'Content Types','/ui/v1.0/data/view/api_portal_content_type/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (7,1,'File','/ui/v1.0/data/view/api_file/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (8,1,'Contents','/ui/v1.0/data/view/api_portal_content/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (9,1,'Settings','/ui/v1.0/data/view/api_setting/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (10,1,'Portal Hosts','/ui/v1.0/data/view/api_portal_host/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (11,1,'Fields','/ui/v1.0/data/view/api_table_field/default',1,1);

/*
End APP
*/

CREATE TABLE IF NOT EXISTS api_file(
    id int NOT NULL AUTO_INCREMENT COMMENT 'Unique ID',
    name varchar(100) NOT NULL COMMENT 'Unique name',
    size int NOT NULL DEFAULT '0',
    mime_type varchar(100) NOT NULL,
    path text NOT NULL COMMENT '',
    path_hash varchar(128) NOT NULL COMMENT '',
    description text NULL,
    file LONGBLOB NOT NULL COMMENT 'BLOB data',
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    UNIQUE KEY(path_hash),
    INDEX(name),
    INDEX(path_hash)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS api_setting (
    id int NOT NULL AUTO_INCREMENT COMMENT 'Unique ID',
    setting varchar(250) NOT NULL,
    value varchar(250) NOT NULL,
    description varchar(50) NOT NULL,
    solution_id int NOT NULL DEFAULT'1',
    FOREIGN KEY(solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    UNIQUE KEY(setting)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO api_setting(setting,value,description,solution_id) VALUES ('portal.default_portal','default','Default portal_id',1);


/* Dataviews */
DELETE FROM api_table_view  WHERE solution_id=1;

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
            <condition field="id" alias="s" value="$$query$$" operator=" like "/>
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


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
23,'LISTVIEW','default',18,'id',1,'<restapi type="select">
    <table name="api_portal_content_type" alias="t"/>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="name" table_alias="t" alias="name"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
24,'SELECTVIEW','default',18,'id',1,'<restapi type="select">
    <table name="api_portal_content_type" alias="t"/>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="name" table_alias="t" alias="name"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
25,'LISTVIEW','default',19,'id',1,'<restapi type="select">
    <table name="api_portal_content" alias="t"/>
    <filter type="or">
        <condition field="name" alias="t" value="$$query$$" operator="$$operator$$"/>
    </filter>
    <joins>
        <join type="inner" table="api_portal" alias="p" condition="t.portal_id=p.id"/>
    </joins>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="name" table_alias="t" alias="Name"/>
        <field name="name" table_alias="p" alias="Portal"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
26,'SELECTVIEW','default',19,'id',1,'<restapi type="select">
    <table name="api_portal_content" alias="t"/>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="name" table_alias="t" alias="name"/>
    </select>
</restapi>');


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
27,'LISTVIEW','default',20,'id',1,'<restapi type="select">
    <table name="api_file" alias="a"/>
    <filter type="or">
        <condition field="name" alias="a" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="a" alias="id"/>
        <field name="name" table_alias="a" alias="Name"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
28,'SELECTVIEW','default',20,'id',1,'<restapi type="select">
    <table name="api_file" alias="a"/>
    <select>
        <field name="id" table_alias="a" alias="id"/>
        <field name="name" table_alias="a" alias="name"/>
    </select>
</restapi>');


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
29,'LISTVIEW','default',21,'id',1,'<restapi type="select">
    <table name="api_setting" alias="a"/>
    <filter type="or">
        <condition field="setting" alias="a" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="a" alias="id"/>
        <field name="setting" table_alias="a" alias="Setting"/>
        <field name="Value" table_alias="a" alias="Value"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
30,'SELECTVIEW','default',21,'id',1,'<restapi type="select">
    <table name="api_setting" alias="a"/>
    <select>
        <field name="id" table_alias="a" alias="id"/>
        <field name="setting" table_alias="a" alias="Setting"/>
    </select>
</restapi>');


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
31,'LISTVIEW','default',22,'id',1,'<restapi type="select">
    <table name="api_portal_host" alias="ph"/>
    <filter type="or">
        <condition field="host" alias="ph" value="$$query$$" operator=" like "/>
    </filter>
    <select>
        <field name="id" table_alias="ph" alias="id"/>
        <field name="host" table_alias="ph" alias="Host"/>
        <field name="portal_id" table_alias="ph" alias="Portal"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
32,'SELECTVIEW','default',21,'id',1,'<restapi type="select">
    <table name="api_portal_host" alias="ph"/>
    <select>
        <field name="id" table_alias="ph" alias="id"/>
        <field name="host" table_alias="ph" alias="Name"/>
    </select>
</restapi>');




INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
33,'LISTVIEW','default',13,'id',1,'<restapi type="select">
    <table name="api_table_field" alias="f"/>
    <joins>
        <join type="inner" table="api_table" alias="t" condition="t.id=f.table_id"/>
    </joins>
    <filter type="or">
        <condition field="alias" alias="t" value="$$query$$" operator="$$operator$$"/>
    </filter>
    <select>
        <field name="id" table_alias="f" alias="id"/>
        <field name="alias" table_alias="t" alias="Tablealias"/>
        <field name="label" table_alias="f" alias="Label"/>
        <field name="name" table_alias="f" alias="Fieldname"/>
    </select>
</restapi>');
