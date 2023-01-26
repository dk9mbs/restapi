

DROP PROCEDURE IF EXISTS api_proc_create_table_field_instance;
DROP PROCEDURE IF EXISTS api_proc_logger;
delimiter //

CREATE PROCEDURE api_proc_logger(IN title varchar(100), IN msg text)
BEGIN
    SELECT concat(title,'\n| =======================\n| ',msg) AS logger;
END//


CREATE PROCEDURE api_proc_create_table_field_instance(IN pitable_id int,
                                                    IN pipos int,
                                                    IN piname varchar(250),
                                                    IN pilabel varchar(50),
                                                    IN pitype_id varchar(50),
                                                    IN picontrol_id int,
                                                    IN picontrol_config text,
                                                    OUT poid int)
BEGIN
    set poid = -1;

    IF EXISTS (SELECT * FROM api_table_field WHERE table_id=pitable_id AND name=piname) THEN
        call api_proc_logger("Field instance exists", CONCAT( 'name:', CONVERT(piname, char), " table_id:", CONVERT(pitable_id, char)) );
        SELECT id INTO poid FROM api_table_field WHERE table_id=pitable_id AND name=piname LIMIT 1;

        UPDATE api_table_field set pos=pipos,name=piname,label=pilabel,control_id=picontrol_id,control_config=picontrol_config
            WHERE id=poid AND provider_id='MANUFACTURER';

    ELSE
        call api_proc_logger("Field instance not exists", CONCAT( 'name:', CONVERT(piname, char), " table_id:", CONVERT(pitable_id, char)) );
        INSERT INTO api_table_field (pos, table_id,name,label,type_id,control_id,control_config)
            VALUES
            (pipos, pitable_id, piname, pilabel, pitype_id, picontrol_id, picontrol_config);
        SELECT LAST_INSERT_ID() INTO poid;
    END IF;
END//
delimiter ;


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


CREATE TABLE IF NOT EXISTS api_table_field_type(
    id varchar(50) NOT NULL,
    name varchar(50) NOT NULL,
    control_id int NOT NULL DEFAULT '0' COMMENT 'Default control id for the ui',
    FOREIGN KEY (control_id) REFERENCES api_table_field_control(id),
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_table_field_type ADD COLUMN IF NOT EXISTS control_id int NOT NULL DEFAULT '1' COMMENT '';
ALTER TABLE api_table_field_type ADD CONSTRAINT FOREIGN KEY IF NOT EXISTS (control_id) REFERENCES api_table_field_control (id);


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

CREATE TABLE IF NOT EXISTS api_provider(
    id varchar(50) NOT NULL,
    name varchar(50) NOT NULL,
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS api_table_field(
    id int NOT NULL AUTO_INCREMENT,
    pos int NOT NULL DEFAULT '10' COMMENT 'Position for ui forms',
    table_id int NOT NULL COMMENT 'ID from the sourcetable',
    label varchar(50) NOT NULL COMMENT 'Label/Columnheader for listviews and forms',
    name varchar(250) NOT NULL COMMENT 'Fieldname (source)',
    is_lookup smallint NOT NULL DEFAULT '0' COMMENT '0=No 1=YES',
    is_virtual smallint NOT NULL DEFAULT '0' COMMENT 'Virtual field not exists on the database',
    type_id varchar(50) NOT NULL COMMENT 'type of field',
    size int NOT NULL DEFAULT '0' COMMENT 'the size in case of string',
    allow_null smallint NOT NULL DEFAULT '0',
    default_value varchar(250) NULL,
    referenced_table_name varchar(250) NULL COMMENT 'referenced table name',
    referenced_table_id int NULL COMMENT 'api_table id',
    referenced_field_name varchar(250) NULL COMMENT 'Field from the referenced table',
    control_id int NULL COMMENT 'control_id',
    control_config text NOT NULL COMMENT 'Overwrite the type config',
    provider_id varchar(50) NOT NULL DEFAULT 'MANUFACTURER',
    UNIQUE KEY(table_id, name),
    FOREIGN KEY(table_id) REFERENCES api_table(id),
    FOREIGN KEY(type_id) REFERENCES api_table_field_type(id),
    FOREIGN KEY(control_id) REFERENCES api_table_field_control(id),
    FOREIGN KEY(provider_id) REFERENCES api_provider(id),
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS referenced_table_id int NULL COMMENT 'api_table id' AFTER referenced_table_name;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS is_virtual smallint NOT NULL DEFAULT '0' COMMENT 'Virtual field not exists on the database' AFTER is_lookup;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS provider_id varchar(50) NOT NULL DEFAULT 'MANUFACTURER' COMMENT 'overwrite with updates' AFTER control_config;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS pos int NOT NULL DEFAULT '10' COMMENT 'Position for ui forms' AFTER id;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS control_id int NULL COMMENT 'control_id';
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS control_config text NOT NULL COMMENT 'Overwrite the type config';
ALTER TABLE api_table_field ADD FOREIGN KEY(control_id) REFERENCES api_table_field_control(id);
ALTER TABLE api_table_field ADD FOREIGN KEY(provider_id) REFERENCES api_provider(id);

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

CREATE TABLE IF NOT EXISTS api_group (
    id int NOT NULL AUTO_INCREMENT,
    groupname varchar(100) NOT NULL,
    is_admin smallint NOT NULL DEFAULT '0',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    UNIQUE KEY(groupname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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

CREATE TABLE IF NOT EXISTS api_event_handler (
    id int NOT NULL AUTO_INCREMENT,
    plugin_module_name varchar(500) NOT NULL COMMENT 'Namespace to the register function',
    publisher varchar(250) NOT NULL COMMENT 'Tablename or publisher of the event',
    event varchar(250) NOT NULL COMMENT 'name of trigger like insert or update',
    type varchar(50) NOT NULL,
    sorting int NOT NULL DEFAULT '100' COMMENT 'Sorting',
    solution_id int NOT NULL DEFAULT '1',
    run_async smallint NOT NULL DEFAULT '0' COMMENT '-1: run async 0=not async',
    run_queue smallint NOT NULL DEFAULT '0' COMMENT '-1: enabled 0=disabled run via timerservice',
    is_enabled smallint NOT NULL DEFAULT '-1' COMMENT '-1: enabled 0=disabled',
    config text NULL COMMENT 'locale event handler config',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    FOREIGN KEY(type) REFERENCES api_event_type(id),
    INDEX (publisher, event),
    INDEX (publisher, event, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS run_async smallint NOT NULL DEFAULT '0' COMMENT '-1: run async 0=not async' AFTER solution_id;
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS is_enabled smallint NOT NULL DEFAULT '-1' COMMENT '-1: enabled 0=disabled' AFTER run_async;
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS run_queue smallint NOT NULL DEFAULT '0' COMMENT '-1: enabled 0=disabled run via timerservice' AFTER run_async;

ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS run_async smallint NOT NULL default '0' COMMENT '-1: run async 0=not async';
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS config text NULL COMMENT 'locale event handler config';


CREATE TABLE IF NOT EXISTS api_process_log_status(
    id int NOT NULL,
    name varchar(100) NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS api_process_log;

CREATE TABLE IF NOT EXISTS api_process_log (
    id varchar(36) NOT NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    status_id int NOT NULL DEFAULT '0'  COMMENT '0=pending 10=ok 20=Error 30=Timeout',
    status_info text NULL COMMENT 'Status info set by the plugin',
    error_text text NULL COMMENT 'in case of an exception',
    response_code int NULL COMMENT 'HTTP Code',
    request_msg longtext NULL COMMENT 'HTTP Request body',
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

/* Bugfixing api_process_log */
ALTER TABLE api_process_log MODIFY request_msg LONGTEXT;
ALTER TABLE api_process_log ADD COLUMN IF NOT EXISTS status_info text NULL COMMENT 'Status info set by the plugin' AFTER status_id;

/* Bugfixing api_process_log */


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


CREATE TABLE IF NOT EXISTS api_file_import_definition(
    id varchar(50) NOT NULL,
    name varchar(100) NOT NULL,
    file_type varchar(50) NOT NULL DEFAULT 'CSV',
    charset varchar(50) NOT NULL DEFAULT 'UTF-8',
    col_seperator varchar(10) NOT NULL DEFAULT ';',
    row_seperator varchar(10) NOT NULL DEFAULT '\n',
    col_header smallint NOT NULL DEFAULT '-1',
    root_node varchar(50) NOT NULL DEFAULT 'ROOT' COMMENT 'For XML files',
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


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

CREATE TABLE IF NOT EXISTS api_portal_host(
    id int NOT NULL AUTO_INCREMENT,
    host varchar(250) NOT NULL,
    portal_id varchar(50) NOT NULL,
    PRIMARY KEY(id),
    UNIQUE KEY(host),
    FOREIGN KEY(portal_id) REFERENCES api_portal(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS api_portal_content_type(
    id int NOT NULL,
    name varchar(50) NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id),
    created_on datetime NOT NULL DEFAULT current_timestamp,
    FOREIGN KEY(solution_id) REFERENCES api_solution(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS api_portal_content(
    id int NOT NULL AUTO_INCREMENT,
    portal_id varchar(100) NOT NULL,
    name varchar(50) NOT NULL,
    title varchar(250) NOT NULL,
    file_path text NULL,
    type_id int NOT NULL,
    content text NULL COMMENT 'Please fill here your page content',
    is_active smallint NOT NULL DEFAULT '-1',
    solution_id int NOT NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    FOREIGN KEY(solution_id) REFERENCES api_solution(id),
    FOREIGN KEY(type_id) REFERENCES api_portal_content_type(id),
    FOREIGN KEY(portal_id) REFERENCES api_portal(id),
    UNIQUE KEY(name,portal_id,type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_portal_content AUTO_INCREMENT=1000000;

ALTER TABLE api_portal_content ADD COLUMN IF NOT EXISTS is_active smallint NOT NULL DEFAULT '-1' AFTER content;
ALTER TABLE api_portal_content ADD COLUMN IF NOT EXISTS title varchar(250) NOT NULL AFTER name;
ALTER TABLE api_portal_content ADD COLUMN IF NOT EXISTS file_path text NULL AFTER title;

/* end portal */


CREATE TABLE IF NOT EXISTS api_table_view_type(
    id varchar(10) NOT NULL,
    name varchar(50) NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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

CREATE TABLE IF NOT EXISTS api_ui_app_nav_item_type(
    id int NOT NULL AUTO_INCREMENT,
    name varchar(50) NOT NULL,
    solution_id int NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (solution_id) REFERENCES api_solution(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE api_ui_app_nav_item_type AUTO_INCREMENT=1000000;

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

