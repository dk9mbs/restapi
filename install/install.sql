

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
        /* call api_proc_logger("Field instance exists", CONCAT( 'name:', CONVERT(piname, char), " table_id:", CONVERT(pitable_id, char)) ); */
        SELECT id INTO poid FROM api_table_field WHERE table_id=pitable_id AND name=piname LIMIT 1;

        UPDATE api_table_field set pos=pipos,name=piname,label=pilabel,control_id=picontrol_id,control_config=picontrol_config
            WHERE id=poid AND provider_id='MANUFACTURER';

    ELSE
        /* call api_proc_logger("Field instance not exists", CONCAT( 'name:', CONVERT(piname, char), " table_id:", CONVERT(pitable_id, char)) );*/
        INSERT INTO api_table_field (pos, table_id,name,field_name,label,type_id,control_id,control_config)
            VALUES
            (pipos, pitable_id, piname,piname, pilabel, pitype_id, picontrol_id, picontrol_config);
        SELECT LAST_INSERT_ID() INTO poid;
    END IF;
END//
delimiter ;

/*
Record based security core function
*/
DROP FUNCTION IF EXISTS api_fn_rec_permission;
DELIMITER //

CREATE FUNCTION api_fn_rec_permission (
    user_name varchar(50), 
    table_alias varchar(50), 
    record_id varchar(50),
    mode varchar(50)
)
RETURNS INT
BEGIN
    DECLARE permission int;
    DECLARE table_id int;
    DECLARE user_id int;

    SELECT id INTO user_id FROM api_user WHERE username=user_name;
    SELECT id INTO table_id FROM api_table WHERE alias=table_alias;

    select p.id INTO permission from api_group_rec_permission p 
        INNER JOIN api_user_group ug ON ug.group_id=p.group_id
        WHERE ug.user_id=user_id 
            AND p.table_id=table_id 
            AND p.record_id_int=record_id 
            AND p.mode_read=-1 LIMIT 1;

    RETURN permission;
END; //
DELIMITER ;

/*
select id,api_fn_rec_permission('root','api_file',id, 'READ') AS group_rec_permission_id from api_file 
    WHERE api_fn_rec_permission('root','api_file',id, 'READ')>0;
*/

CREATE TABLE IF NOT EXISTS dummy (
    id int NOT NULL auto_increment,
    name varchar(50) NOT NULL,
    Port int NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/* api_provider */
CREATE TABLE IF NOT EXISTS api_provider(
    id varchar(50) NOT NULL,
    name varchar(50) NOT NULL,
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


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
    orm_classname varchar(100) NOT NULL DEFAULT 'services.orm.Field.DefaultField' COMMENT 'Name of the orm mapper class',
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_table_field_type ADD COLUMN IF NOT EXISTS control_id int NOT NULL DEFAULT '1' COMMENT '';
ALTER TABLE api_table_field_type ADD CONSTRAINT FOREIGN KEY IF NOT EXISTS (control_id) REFERENCES api_table_field_control (id);
ALTER TABLE api_table_field_type ADD COLUMN IF NOT EXISTS
    orm_classname varchar(100) NOT NULL DEFAULT 'services.orm.Field.DefaultField' COMMENT 'Name of the orm mapper class';


CREATE TABLE IF NOT EXISTS api_table (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(250) NOT NULL DEFAULT '',
    alias varchar(250) NOT NULL,
    table_name varchar(250) NOT NULL,
    id_field_name varchar(250) NOT NULL,
    id_field_type varchar(50) NOT NULL COMMENT 'String,Int',
    desc_field_name varchar(250) NOT NULL COMMENT 'Name of the description field',
    enable_audit_log smallint NOT NULL DEFAULT '0',
    enable_record_permission smallint NOT NULL DEFAULT '0' COMMENT '0=disabled -1=enabled',
    enable_dms smallint NOT NULL DEFAULT '0' COMMENT 'Activate DMS for this table',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    FOREIGN KEY(id_field_type) REFERENCES api_table_field_type(id),
    PRIMARY KEY(id),
    UNIQUE KEY(alias),
    UNIQUE KEY(table_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_table ADD COLUMN IF NOT EXISTS name varchar(250) NOT NULL DEFAULT '' AFTER id;
ALTER TABLE api_table ADD COLUMN IF NOT EXISTS enable_record_permission smallint NOT NULL DEFAULT '0' COMMENT '' AFTER enable_audit_log;
ALTER TABLE api_table ADD COLUMN IF NOT EXISTS enable_dms smallint NOT NULL DEFAULT '0' COMMENT 'Activate DMS for this table' AFTER enable_record_permission;

/* formatter */
CREATE TABLE IF NOT EXISTS api_data_formatter_type(
    id int NOT NULL COMMENT '',
    name varchar(50) NOT NULL COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS api_data_formatter(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    name varchar(100) NOT NULL COMMENT '',
    table_id int NULL COMMENT '',
    template_header text NULL COMMENT 'Jinja header template',
    template_line text NULL COMMENT 'Jinja body template',
    template_footer text NULL COMMENT 'Jinja footer template',
    template_file varchar(250) NULL COMMENT 'Template File (Jinja)',
    line_separator varchar(5) NULL COMMENT 'Line seperatur',
    file_name varchar(250) NULL COMMENT 'Filename in case of download the file',
    content_disposition varchar(50) NULL COMMENT 'Using in http header',
    type_id int NOT NULL,
    mime_type varchar(100) NOT NULL DEFAULT 'application/text',
    page_mode varchar(50) NULL COMMENT 'Pagemode for Jinja file base templates',
    provider_id varchar(50) NOT NULL DEFAULT 'MANUFACTURER',
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    FOREIGN KEY(type_id) REFERENCES api_data_formatter_type(id),
    FOREIGN KEY(table_id) REFERENCES api_table(id),
    FOREIGN KEY(provider_id) REFERENCES api_provider(id),
    UNIQUE KEY(name, table_id, type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_data_formatter ADD COLUMN IF NOT EXISTS  mime_type varchar(100) NOT NULL DEFAULT 'text/html' AFTER type_id;
ALTER TABLE api_data_formatter ADD COLUMN IF NOT EXISTS  provider_id varchar(50) NOT NULL DEFAULT 'MANUFACTURER' AFTER type_id;
ALTER TABLE api_data_formatter ADD COLUMN IF NOT EXISTS  line_separator varchar(5) NULL COMMENT 'Line seperatur' AFTER template_footer;
ALTER TABLE api_data_formatter ADD COLUMN IF NOT EXISTS  file_name varchar(250) NULL COMMENT 'Filename in case of download the file' AFTER line_separator;
ALTER TABLE api_data_formatter ADD COLUMN IF NOT EXISTS  content_disposition varchar(50) NULL COMMENT 'Using in http header' AFTER file_name;
ALTER TABLE api_data_formatter ADD COLUMN IF NOT EXISTS  template_file varchar(250) NULL COMMENT 'Template File (Jinja)' AFTER template_footer;
ALTER TABLE api_data_formatter ADD COLUMN IF NOT EXISTS page_mode varchar(50) NULL COMMENT 'Pagemode for Jinja file base templates' AFTER mime_type;

ALTER TABLE api_data_formatter ADD FOREIGN KEY IF NOT EXISTS (provider_id) REFERENCES api_provider(id);
ALTER TABLE api_data_formatter ADD UNIQUE KEY IF NOT EXISTS (name, table_id, type_id);

CREATE TABLE IF NOT EXISTS api_table_field(
    id int NOT NULL AUTO_INCREMENT,
    pos int NOT NULL DEFAULT '10' COMMENT 'Position for ui forms',
    table_id int NOT NULL COMMENT 'ID from the sourcetable',
    label varchar(50) NOT NULL COMMENT 'Label/Columnheader for listviews and forms',
    name varchar(250) NOT NULL COMMENT 'Fieldname (source)',
    field_name varchar(250) NULL COMMENT 'Pyhs. fieldname',
    is_lookup smallint NOT NULL DEFAULT '0' COMMENT '0=No 1=YES',
    is_virtual smallint NOT NULL DEFAULT '0' COMMENT 'Virtual field not exists on the database',
    is_primary_key smallint NOT NULL DEFAULT '0' COMMENT 'Primary KEY Col',
    type_id varchar(50) NOT NULL COMMENT 'type of field',
    size int NOT NULL DEFAULT '0' COMMENT 'the size in case of string',
    allow_null smallint NOT NULL DEFAULT '0',
    default_value varchar(250) NULL,
    referenced_table_name varchar(250) NULL COMMENT 'referenced table name',
    referenced_table_id int NULL COMMENT 'api_table id',
    referenced_field_name varchar(250) NULL COMMENT 'Field from the referenced table',
    control_id int NULL COMMENT 'control_id',
    formatter varchar(250) NULL COMMENT 'Formatter',
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
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS field_name varchar(250) NULL COMMENT 'Pyhs. fieldname' AFTER name;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS is_virtual smallint NOT NULL DEFAULT '0' COMMENT 'Virtual field not exists on the database' AFTER is_lookup;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS provider_id varchar(50) NOT NULL DEFAULT 'MANUFACTURER' COMMENT 'overwrite with updates' AFTER control_config;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS pos int NOT NULL DEFAULT '10' COMMENT 'Position for ui forms' AFTER id;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS control_id int NULL COMMENT 'control_id';
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS control_config text NOT NULL COMMENT 'Overwrite the type config';
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS is_primary_key smallint NOT NULL DEFAULT '0' COMMENT 'Primary KEY Col' AFTER is_virtual;
ALTER TABLE api_table_field ADD COLUMN IF NOT EXISTS formatter varchar(250) NULL COMMENT 'Formatter' AFTER control_id;

/* in allen datenbanken ausgerollt */
/*ALTER TABLE api_table_field ADD FOREIGN KEY IF NOT EXISTS (control_id) REFERENCES api_table_field_control(id);
ALTER TABLE api_table_field ADD FOREIGN KEY IF NOT EXISTS (provider_id) REFERENCES api_provider(id);*/


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

CREATE TABLE IF NOT EXISTS api_user_apikey (
    id varchar(100) NOT NULL,
    user_id int NOT NULL,
    name varchar(50) NOT NULL,
    disabled smallint NOT NULL DEFAULT '0',
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES api_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS api_group (
    id int NOT NULL AUTO_INCREMENT,
    groupname varchar(100) NOT NULL,
    is_admin smallint NOT NULL DEFAULT '0',
    user_id int NULL COMMENT 'private group if user_id not is null',
    solution_id int NOT NULL DEFAULT '1',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    FOREIGN KEY (user_id) REFERENCES api_user(id),
    CONSTRAINT `foreign_reference_api_group_user_id_api_user` FOREIGN KEY (user_id) REFERENCES api_user(id),
    PRIMARY KEY(id),
    UNIQUE KEY(groupname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_group ADD COLUMN IF NOT EXISTS user_id int NULL COMMENT 'private group if user_id not is null' AFTER is_admin;
ALTER TABLE api_group ADD CONSTRAINT `foreign_reference_api_group_user_id_api_user` FOREIGN KEY IF NOT EXISTS (user_id) REFERENCES api_user(id);

ALTER TABLE api_group AUTO_INCREMENT=900000000;

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

CREATE TABLE IF NOT EXISTS api_group_rec_permission_type(
    id int NOT NULL AUTO_INCREMENT,
    name varchar(50) NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE api_group_rec_permission_type AUTO_INCREMENT=900000000;

DROP TABLE IF EXISTS api_group_record_permission;
CREATE TABLE IF NOT EXISTS api_group_rec_permission(
    id int NOT NULL AUTO_INCREMENT,
    type_id int NOT NULL DEFAULT '1',
    group_id int NOT NULL COMMENT 'user group id',
    table_id int NOT NULL COMMENT 'table id',
    record_id_str varchar(50) NULL COMMENT 'string based recordid',
    record_id_int int NULL COMMENT 'integer based recordid',
    mode_read smallint NOT NULL DEFAULT '0' COMMENT 'read',
    mode_update smallint NOT NULL DEFAULT '0' COMMENT 'update',
    mode_delete smallint NOT NULL DEFAULT '0' COMMENT 'delete',
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    FOREIGN KEY(group_id) REFERENCES api_group(id),
    FOREIGN KEY(table_id) REFERENCES api_table(id),
    FOREIGN KEY(type_id) REFERENCES api_group_rec_permission_type(id),
    UNIQUE KEY(group_id, table_id, record_id_str),
    UNIQUE KEY(group_id, table_id, record_id_int)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


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

CREATE TABLE IF NOT EXISTS api_event_handler_status(
    id varchar(10) NOT NULL,
    name varchar(50) NOT NULL,
    is_running smallint NOT NULL DEFAULT '0',
    is_waiting smallint NOT NULL DEFAULT '0',
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
    status_id varchar(10) NULL COMMENT 'Waitung or Running only for single instance',
    is_single_instance smallint NOT NULL DEFAULT '0' COMMENT 'Can only execute one per time',
    config text NULL COMMENT 'locale event handler config',
    inline_code text NULL COMMENT 'inline python code to execute',
    FOREIGN KEY (solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id),
    FOREIGN KEY(type) REFERENCES api_event_type(id),
    FOREIGN KEY(status_id) REFERENCES api_event_handler_status(id),
    INDEX (publisher, event),
    INDEX (publisher, event, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS run_async smallint NOT NULL DEFAULT '0' COMMENT '-1: run async 0=not async' AFTER solution_id;
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS is_enabled smallint NOT NULL DEFAULT '-1' COMMENT '-1: enabled 0=disabled' AFTER run_async;
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS run_queue smallint NOT NULL DEFAULT '0' COMMENT '-1: enabled 0=disabled run via timerservice' AFTER run_async;
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS run_async smallint NOT NULL default '0' COMMENT '-1: run async 0=not async' AFTER solution_id;
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS config text NULL COMMENT 'locale event handler config' AFTER is_enabled;
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS inline_code text NULL COMMENT 'inline python code to execute' AFTER config;

ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS status_id varchar(10) NULL COMMENT 'Waitung or Running only for single instance' AFTER is_enabled;
ALTER TABLE api_event_handler ADD COLUMN IF NOT EXISTS is_single_instance smallint NOT NULL DEFAULT '0' COMMENT 'Can only execute one per time' AFTER status_id;
ALTER TABLE api_event_handler ADD CONSTRAINT `event_handler_event_handler_status` FOREIGN KEY IF NOT EXISTS (status_id) REFERENCES api_event_handler_status(id);


DROP TABLE IF EXISTS api_table_action;
CREATE TABLE IF NOT EXISTS api_table_action(
    id int NOT NULL AUTO_INCREMENT,
    table_id INT NOT NULL,
    event_handler_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    position int NOT NULL DEFAULT '100',
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE api_table_action AUTO_INCREMENT=900000000;


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
    template text NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(solution_id) REFERENCES api_solution(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_portal ADD COLUMN IF NOT EXISTS name varchar(100);
ALTER TABLE api_portal ADD COLUMN IF NOT EXISTS solution_id int NOT NULL;
ALTER TABLE api_portal ADD COLUMN IF NOT EXISTS template text NULL;
ALTER TABLE api_portal ADD FOREIGN KEY IF NOT EXISTS (solution_id) REFERENCES api_solution(id);


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
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    name varchar(100) NOT NULL DEFAULT '<NEW>' COMMENT '',
    type_id varchar(10) NOT NULL COMMENT 'LISTVIEW,SELECTVIEW,FORMVIEW',
    table_id int NOT NULL COMMENT '',
    id_field_name varchar(50) NOT NULL COMMENT '',
    fetch_xml text NOT NULL COMMENT '',
    columns text NULL COMMENT 'List columns (JSON)' COMMENT '',
    solution_id int NOT NULL COMMENT '',
    PRIMARY KEY(id),
    UNIQUE KEY(table_id, type_id, name),
    FOREIGN KEY(table_id) REFERENCES api_table(id),
    FOREIGN KEY(solution_id) REFERENCES api_solution(id),
    FOREIGN KEY(type_id) REFERENCES api_table_view_type(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_table_view ADD column IF NOT EXISTS columns text NULL COMMENT 'List columns (JSON)' AFTER fetch_xml;

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

CREATE TABLE IF NOT EXISTS api_permission_log(
    id int NOT NULL AUTO_INCREMENT,
    log_type nvarchar(50) NOT NULL,
    table_name varchar(250) NULL,
    table_alias varchar(250) NULL,
    username varchar(100) NOT NULL,
    mode varchar(50) NOT NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


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
    file LONGBLOB NULL COMMENT 'BLOB data',
    text LONGTEXT NULL COMMENT 'Text based blob data',
    mode varchar(10) NOT NULL DEFAULT 'file' COMMENT 'file, text',
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    UNIQUE KEY(path_hash),
    INDEX(name),
    INDEX(path_hash)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE api_file MODIFY COLUMN file LONGBLOB NULL COMMENT 'Binary blob data';
ALTER TABLE api_file ADD COLUMN IF NOT EXISTS text LONGTEXT NULL COMMENT 'Text based blob data' AFTER file;
ALTER TABLE api_file ADD COLUMN IF NOT EXISTS mode varchar(10) NOT NULL DEFAULT 'file' COMMENT 'file, text' after text;

DROP TRIGGER IF EXISTS api_file_before_insert;
DROP TRIGGER IF EXISTS api_file_before_update;
delimiter //
create trigger api_file_before_insert before insert on api_file
for each row
begin
   if (NEW.path_hash is null or NEW.path_hash='' ) then
      set NEW.path_hash=password(NEW.path);
   end if;
end
//
delimiter ;

delimiter //
create trigger api_file_before_update before update on api_file
for each row
begin
    set NEW.path_hash=password(NEW.path);
end
//
delimiter ;




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
ALTER TABLE api_setting AUTO_INCREMENT=900000000;

CREATE TABLE IF NOT EXISTS api_mqtt_message_bus(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    topic varchar(500) NOT NULL COMMENT '',
    regex varchar(500) NOT NULL COMMENT '',
    alias varchar(500) NULL COMMENT '',
    is_enabled smallint NOT NULL DEFAULT '-1' COMMENT '',
    solution_id int NOT NULL DEFAULT'1',
    FOREIGN KEY(solution_id) REFERENCES api_solution(id),
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE api_mqtt_message_bus AUTO_INCREMENT=900000000;

/* EMail */
--ALTER TABLE api_file DROP FOREIGN KEY IF EXISTS foreign_reference_api_email;
--DROP TABLE IF EXISTS api_email_header;
--DROP TABLE IF EXISTS api_email_part;
--DROP TABLE IF EXISTS api_email;


CREATE TABLE IF NOT EXISTS api_email_mailbox_type(
    id varchar(10) NOT NULL COMMENT '',
    name varchar(50) NOT NULL COMMENT '',
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE api_email_mailbox_type AUTO_INCREMENT=900000000;

CREATE TABLE IF NOT EXISTS api_email_mailbox(
    id varchar(10) NOT NULL COMMENT '',
    name varchar(100) NOT NULL COMMENT '',
    type_id varchar(10) NOT NULL COMMENT '',
    username varchar(100) NOT NULL COMMENT '',
    password varchar(100) NOT NULL COMMENT '',
    imap_folder varchar(250) NULL DEFAULT 'INBOX' COMMENT '',
    imap_server varchar(250) NULL COMMENT '',
    imap_imported_folder varchar(250) NULL COMMENT 'Copy the mail to target folder after import',
    imap_error_folder varchar(25) NULL COMMENT 'Copy all doublets (message_id) in this folder',
    imap_delete smallint NOT NULL DEFAULT '0' COMMENT 'Delete mail after import',
    imap_port int NULL DEFAULT '993',
    smtp_server varchar(250) NULL COMMENT '',
    smtp_port int NULL DEFAULT '587',
    is_enabled smallint NOT NULL DEFAULT'-1' COMMENT '',
    PRIMARY KEY(id),
    FOREIGN KEY(type_id) REFERENCES api_email_mailbox_type(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS api_email(
    id int NOT NULL AUTO_INCREMENT,
    mailbox_id varchar(10) NOT NULL,
    message_id varchar(250) NULL COMMENT 'in case of outgoing mail null',
    message_uid int NULL COMMENT 'uid from imap server',
    message_from varchar(250) NOT NULL,
    message_to text NULL,
    folder varchar(250) NOT NULL,
    subject text NULL,
    content_type varchar(100) NULL,
    body longtext NULL,
    spam_level varchar(50) NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    FOREIGN KEY(mailbox_id) REFERENCES api_email_mailbox(id),
    UNIQUE KEY (mailbox_id, message_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS api_email_part(
    id int NOT NULL AUTO_INCREMENT,
    email_id int not NULL,
    content_type varchar(100) NULL,
    content_disposition varchar(50) NULL,
    body longtext NULL,
    created_on datetime NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(id),
    FOREIGN KEY(email_id) REFERENCES api_email(id) ON DELETE CASCADE
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS api_email_header(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    email_id int NOT NULL COMMENT '',
    header_key varchar(50) NOT NULL COMMENT '',
    header_value text NULL COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp,
    FOREIGN KEY(email_id) REFERENCES api_email(id) ON DELETE CASCADE,
    PRIMARY KEY(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


ALTER TABLE api_file ADD column IF NOT EXISTS email_id int NULL COMMENT 'unique id from the email' AFTER file;
ALTER TABLE api_file ADD CONSTRAINT `foreign_reference_api_email` FOREIGN KEY IF NOT EXISTS (email_id) REFERENCES api_email(id) ON DELETE CASCADE;
/* end EMail */

/*
DROP TABLE IF EXISTS api_activity;
DROP TABLE IF EXISTS api_activity_type;
DROP TABLE IF EXISTS api_activity_status;
DROP TABLE IF EXISTS api_activity_lane;
DROP TABLE IF EXISTS api_activity_board;
DROP TABLE IF EXISTS api_record_reference;
DROP TABLE IF EXISTS api_activity_effort_unit;
*/

CREATE TABLE IF NOT EXISTS api_activity_type(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    name varchar(50) NOT NULL COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp COMMENT '',
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE api_activity_type AUTO_INCREMENT=900000000;

CREATE TABLE IF NOT EXISTS api_activity_status(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    name varchar(50) NOT NULL COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp COMMENT '',
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE api_activity_status AUTO_INCREMENT=900000000;

CREATE TABLE IF NOT EXISTS api_activity_board(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    name varchar(50) NOT NULL COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp COMMENT '',
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE api_activity_board AUTO_INCREMENT=900000000;

CREATE TABLE IF NOT EXISTS api_activity_lane(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    board_id int NOT NULL COMMENT '',
    name varchar(50) NOT NULL COMMENT '',
    position int NOT NULL DEFAULT '1000' COMMENT '',    
    created_on datetime NOT NULL DEFAULT current_timestamp COMMENT '',
    PRIMARY KEY(id),
    CONSTRAINT `foreign_reference_api_activity_lane_board` FOREIGN KEY(board_id) REFERENCES api_activity_board(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE api_activity_lane AUTO_INCREMENT=900000000;

CREATE TABLE IF NOT EXISTS api_activity_effort_unit(
    id varchar(10) NOT NULL COMMENT '',
    name varchar(50) NOT NULL COMMENT '',
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS api_activity_sprint_status(
    id int NOT NULL COMMENT '',
    name varchar(50) NOT NULL COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp COMMENT '',
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS api_activity_sprint(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    name varchar(250) NOT NULL COMMENT '',
    from_date datetime NULL COMMENT '',
    until_date datetime NULL COMMENT '',
    status_id int NOT NULL DEFAULT '100' COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp COMMENT '',
    CONSTRAINT `foreign_reference_api_activity_sprint_id` FOREIGN KEY(status_id) REFERENCES api_activity_sprint_status(id),
    PRIMARY KEY(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS api_activity(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    type_id int NOT NULL DEFAULT '1' COMMENT '', 
    board_id int NOT NULL DEFAULT '1' COMMENT '',
    lane_id int NOT NULL DEFAULT '1' COMMENT '',
    status_id int NOT NULL DEFAULT '1' COMMENT '',
    subject varchar(500) NULL COMMENT '',
    msg_text LONGTEXT NULL COMMENT '',
    planned_effort int NOT NULL DEFAULT '0' COMMENT '',
    actual_effort int NOT NULL DEFAULT '0' COMMENT '',
    effort_unit_id varchar(10) NOT NULL DEFAULT 'day' COMMENT '',
    due_date datetime NULL COMMENT '',
    sprint_id int NULL COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp COMMENT '',
    PRIMARY KEY(id),
    CONSTRAINT `foreign_reference_api_activity_status_id` FOREIGN KEY(status_id) REFERENCES api_activity_status(id),
    CONSTRAINT `foreign_reference_api_activity_type_id` FOREIGN KEY(type_id) REFERENCES api_activity_type(id),
    CONSTRAINT `foreign_reference_api_activity_board_id` FOREIGN KEY(board_id) REFERENCES api_activity_board(id),
    CONSTRAINT `foreign_reference_api_activity_lane_id` FOREIGN KEY(lane_id) REFERENCES api_activity_lane(id),
    CONSTRAINT `foreign_reference_api_activity_effort_unit_id` FOREIGN KEY(effort_unit_id) REFERENCES api_activity_effort_unit(id),
    CONSTRAINT `foreign_reference_api_activity_sprint_id` FOREIGN KEY(sprint_id) REFERENCES api_activity_sprint(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE api_activity ADD column IF NOT EXISTS sprint_id int NULL COMMENT '' AFTER due_date;
ALTER TABLE api_activity ADD CONSTRAINT `foreign_reference_api_activity_sprint_id_to_api_sprint` FOREIGN KEY IF NOT EXISTS (sprint_id) REFERENCES api_activity_sprint(id);

CREATE TABLE IF NOT EXISTS api_record_reference(
    id int NOT NULL AUTO_INCREMENT COMMENT '',
    name varchar(50) NOT NULL DEFAULT '<NEW REFERENCE>' COMMENT '',
    table_id int NOT NULL COMMENT '',
    record_id int NULL COMMENT '',
    record_id_str varchar(50) NULL COMMENT '',
    ref_table_id int NOT NULL COMMENT '',
    ref_record_id int NULL COMMENT '',
    ref_record_id_str varchar(50) NULL COMMENT '',
    created_on datetime NOT NULL DEFAULT current_timestamp COMMENT '',
    PRIMARY KEY(id),
    UNIQUE KEY(table_id, record_id, ref_table_id, ref_record_id),
    UNIQUE KEY(table_id, record_id_str, ref_table_id, ref_record_id_str),
    CONSTRAINT `foreign_reference_api_record_reference_table_id` FOREIGN KEY(table_id) REFERENCES api_table(id),
    CONSTRAINT `foreign_reference_api_record_reference_ref_table_id` FOREIGN KEY(ref_table_id) REFERENCES api_table(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;