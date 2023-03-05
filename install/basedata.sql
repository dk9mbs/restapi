INSERT IGNORE INTO api_solution(id,name) VALUES (1,'restapi');
INSERT IGNORE INTO api_solution(id,name) VALUES (2,'customizing');

INSERT IGNORE INTO api_provider (id, name) VALUES ('MANUFACTURER','Manufacturer');
INSERT IGNORE INTO api_provider (id, name) VALUES ('SELF','Self');

INSERT IGNORE INTO api_data_formatter_type (id,name) VALUES (1,'Record');
INSERT IGNORE INTO api_data_formatter_type (id,name) VALUES (2,'Recordset');


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
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (20,'Dropdown (Feste Liste)','SELECTLIST','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (100,'nicEdit','NIC-EDIT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (101,'ace Edit','ACE-EDIT','{}');
INSERT IGNORE INTO api_table_field_control(id,name,control,control_config) VALUES (200,'SubTable','SUB-TABLE','{}');

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
UPDATE api_table_field_control SET control_config='{}' WHERE id=20;

UPDATE api_table_field_control SET control_config='{}' WHERE id=100;
UPDATE api_table_field_control SET control_config='{}' WHERE id=101;
UPDATE api_table_field_control SET control_config='{}' WHERE id=200;


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
    VALUES (9,'Eventhandler','api_event_handler', 'api_event_handler','id','int','publisher',0);

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

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (26,'Log','api_process_log_status', 'api_process_log_status','id','int','name',0);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (27,'Provider','api_provider', 'api_provider','id','string','name',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (28,'Datei-Import-Definition','api_file_import_definition', 'api_file_import_definition','id','string','name',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (29,'Daten Formatierungs Typen','api_data_formatter_type', 'api_data_formatter_type','id','int','name',-1);

INSERT IGNORE INTO api_table(id,name,alias,table_name,id_field_name,id_field_type,desc_field_name,enable_audit_log)
    VALUES (30,'Daten Formatierungen','api_data_formatter', 'api_data_formatter','id','int','name',-1);


/* Bugfixing */
UPDATE api_table SET id_field_type='string' WHERE id_field_type='String';
UPDATE api_table SET id_field_type='int' WHERE id_field_type='Int';
UPDATE api_table set name=alias WHERE name IS NULL OR name='';
/* */


INSERT IGNORE INTO api_user (id,username,password,disabled,is_admin) VALUES (1,'root','password',0,-1);
INSERT IGNORE INTO api_user (id,username,password,disabled,is_admin) VALUES (99,'system','password',0,-1);
INSERT IGNORE INTO api_user (id,username,password) VALUES (100,'guest','password');

INSERT IGNORE INTO api_group (id,groupname,is_admin) VALUES (1,'sysadmin',-1);
INSERT IGNORE INTO api_group (id,groupname,is_admin) VALUES (100,'guest',0);

INSERT IGNORE INTO api_user_group (user_id,group_id) VALUES (100,100);

INSERT IGNORE INTO api_group_permission (group_id,table_id, mode_read) VALUES (100,1,-1);
INSERT IGNORE INTO api_group_permission (group_id,table_id, mode_read) VALUES (100,8,-1);

INSERT IGNORE INTO api_event_type (id, name) VALUES ('before','On before');
INSERT IGNORE INTO api_event_type (id, name) VALUES ('after','On after');

/* api_process_log */
call api_proc_create_table_field_instance(23,100, 'id','ID','string',1,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,200, 'created_on','Erstellt am','datetime',9,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,300, 'status_id','Status','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,400, 'status_info','Status Info','string',18,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,500, 'error_text','Fehler Text','string',18,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,600, 'response_code','Antwort Code','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,700, 'request_msg','Request','string',18,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,800, 'response_on','Response um','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,900, 'response_msg','Response','int',18,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,1000, 'config','Configuration','int',18,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,1100, 'event_handler_id','Event','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,1200, 'run_async','ID','Asynchron',19,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,1300, 'retries','Wiederholungen','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(23,1400, 'last_retry_on','Letzte Wiederholung um','int',9,'{"disabled": true}', @out_value);

/* setting */
call api_proc_create_table_field_instance(21,100, 'id','ID','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(21,200, 'setting','Einstellung','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(21,300, 'value','Wert','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(21,400, 'description','Beschreibung','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(21,500, 'solution_id','Lösung','int',2,'{"disabled": false}', @out_value);

/* api_data_formatter_type */
call api_proc_create_table_field_instance(29,100, 'id','ID','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(29,200, 'name','Bezeichnung','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(29,300, 'created_on','Erstellt am','datetime',9,'{"disabled": true}', @out_value);

/* api_data_formatter */
call api_proc_create_table_field_instance(30,100, 'id','ID','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(30,200, 'name','Bezeichnung','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(30,300, 'table_id','Tabelle','int',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(30,300, 'type_id','Typ','int',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(30,400, 'mime_type','Mime Typ','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(30,500, 'template_header','Kopf Bereich','string',18,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(30,600, 'template_line','Daten Bereich','string',18,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(30,700, 'template_footer','Fuss Bereich','string',18,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(30,710, 'line_separator','Datensatz Trenner','string',20,
    '{"disabled": false, "listitems":";Kein|@n;New Line(Unix)|@r@n;New Line (Windows)"}', @out_value);
call api_proc_create_table_field_instance(30,720, 'file_name','Dateiname','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(30,730, 'content_disposition','CONTENT_DISPOSITION','string',20,
    '{"disabled": false, "listitems":"inline;inline|attachment;attachment"}', @out_value);
call api_proc_create_table_field_instance(30,800, 'created_on','Erstellt am','datetime',9,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(30,900, 'provider_id','Besitzer','string',2,'{"disabled": false}', @out_value);


/* api_event_handler */
call api_proc_create_table_field_instance(9,100, 'id','ID','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(9,200, 'plugin_module_name','Module','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,300, 'publisher','Publisher','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,400, 'event','Ereignis','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,500, 'type','Typ','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,600, 'sorting','Reihenfolge','int',14,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,700, 'solution_id','Lösung','int',2,'{"disabled": false}', @out_value);
UPDATE api_table_field SET referenced_table_name='api_solution', referenced_table_id=25, referenced_field_name='id', is_lookup=-1 WHERE id=@out_value;
call api_proc_create_table_field_instance(9,800, 'run_async','Asynchron','int',19,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,900, 'run_queue','Queue','int',19,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,1000, 'is_enabled','Aktiv','int',19,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,1100, 'config','Configuration','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(9,1100, 'inline_code','Inline Code','string',101,'{"disabled": false, "mode":"ace/mode/python"}', @out_value);

/* user */
call api_proc_create_table_field_instance(2,100, 'id','ID','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(2,200, 'username','Username','string',1,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(2,300, 'password','Password','string',11,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(2,400, 'disabled','Disabled','int',19,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(2,500, 'is_admin','Admin?','int',19,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(2,600, 'solution_id','Solution','int',2,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(2,600, '__sessions','Sitzungen','string',200,'{}', @out_value);
UPDATE api_table_field
    SET is_virtual=-1, field_name='id',referenced_table_name='api_session',referenced_table_id=7,referenced_field_name='user_id'
    WHERE id=@out_value;

/* dummy */
call api_proc_create_table_field_instance(1,10, 'id','ID','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(1,20, 'name','Name','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(1,30, 'Port','Port','int',14,'{"disabled": false}', @out_value);

/* api_table_field */
call api_proc_create_table_field_instance(13,100, 'id','ID','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(13,200, 'pos','Position','int',14,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,300, 'table_id','Tabellen ID','int',2,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(13,400, 'label','Bezeichnung','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,500, 'name','Name','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,510, 'field_name','Feldname','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,600, 'is_lookup','Lookup?','int',19,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,700, 'type_id','Type','int',2,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(13,800, 'size','Größe','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(13,900, 'allow_null','Null Werte?','int',19,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(13,1000, 'default_value','Default','string',1,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(13,1100, 'referenced_table_name','Ref. Tabelle (Name)','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,1200, 'referenced_table_id','Ref. Tabelle (ID)','int',2,'{"disabled": false}', @out_value);
UPDATE api_table_field SET referenced_table_name='api_table', referenced_table_id=10, referenced_field_name='table_name', is_lookup=-1 WHERE id=@out_value;
call api_proc_create_table_field_instance(13,1300, 'referenced_field_name','Ref. Feldname','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,1400, 'control_id','Control','int',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,1500, 'control_config','Konfiguration','string',18,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,1600, 'provider_id','Provider','string',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(13,1600, 'is_virtual','Virtuelles Feld','int',19,'{"disabled": false}', @out_value);

/* session */
call api_proc_create_table_field_instance(7,100, 'id','ID','string',1,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(7,200, 'user_id','Benutzer','int',2,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(7,300, 'session_values','Werte','string',18,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(7,400, 'created_on','Erstellt am','datetime',9,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(7,500, 'last_access_on','Letzter Zugriff','datetime',9,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(7,600, 'disabled','Disabled','int',19,'{"disabled": false}', @out_value);

/* api_portal_content */
call api_proc_create_table_field_instance(19,100, 'id','ID','int',14,'{"disabled": true, "insert": {"disabled":false}}', @out_value);
call api_proc_create_table_field_instance(19,200, 'portal_id','Portal','int',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(19,300, 'name','Name','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(19,400, 'title','Titel','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(19,600, 'type_id','Typ','int',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(19,700, 'content','Inhalt','string',18,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(19,800, 'is_active','Aktiviert','int',19,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(19,900, 'solution_id','Lösung','int',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(19,1000, 'file_path','Bild Pfad','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(19,1100, 'created_on','Erstellt am','datetime',9,'{"disabled": true}', @out_value);

/* api_table_view */
call api_proc_create_table_field_instance(12,100, 'id','ID','int',14,'{"disabled": true}', @out_value);
call api_proc_create_table_field_instance(12,200, 'name','Name','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(12,300, 'type_id','Type','string',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(12,400, 'table_id','Tabelle','int',2,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(12,500, 'id_field_name','ID Feld Name','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(12,600, 'fetch_xml','FetchXML','string',101,'{"disabled": false,"mode":"ace/mode/xml"}', @out_value);
call api_proc_create_table_field_instance(12,700, 'solution_id','Lösung','int',2,'{"disabled": false}', @out_value);

INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (1,'plugin_test','dummy','insert','before');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (2,'plugin_test','dummy','insert','after');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (3,'plugin_test','dummy','update','before');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type) VALUES (4,'plugin_test','dummy','update','after');
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type,run_async) VALUES (5,'api_http_endpoint','dummy','insert','after',-1);
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type,run_async) VALUES (6,'api_http_endpoint','dummy','update','after',-1);
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type,run_async) VALUES (7,'api_clear_log','$timer_every_ten_minutes','execute','after',0);
INSERT IGNORE INTO api_event_handler(id,plugin_module_name,publisher,event,type,run_async) VALUES (8,'api_clear_session','$timer_every_hour','execute','after',0);

INSERT IGNORE INTO api_process_log_status(id,name) VALUES (0,'Pending');
INSERT IGNORE INTO api_process_log_status(id,name) VALUES (5,'Worker');
INSERT IGNORE INTO api_process_log_status(id,name) VALUES (10,'Success');
INSERT IGNORE INTO api_process_log_status(id,name) VALUES (20,'Error');
INSERT IGNORE INTO api_process_log_status(id,name) VALUES (30,'Timeout');


call api_proc_create_table_field_instance(28,100, 'id','ID','string',1,'{"disabled": false}', @out_value);
call api_proc_create_table_field_instance(28,100, 'name','Bezeichnung','string',1,'{"disabled": false}', @out_value);

UPDATE api_table_field SET field_name=name WHERE field_name IS NULL;

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

<!-- Start Bootstrap -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/js/bootstrap.min.js" integrity="sha384-Atwg2Pkwv9vp0ygtn1JAojH0nYbwNJLPhwyoVbhoPwBhjQPR5VtM2+xf0Uwh9KtT" crossorigin="anonymous"></script>
<!-- End Bootstrap -->

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

</head>
<body>
    <div id="content">
    {{ content }}
    </div>
</body>
</html>' WHERE id='default' AND template IS NULL;


INSERT IGNORE INTO api_portal_host(host,portal_id) VALUES ('subdomain.domain.org','default');

INSERT IGNORE INTO api_portal_content_type(id,name,solution_id) VALUES (1, 'main',1);

UPDATE api_portal_content SET title=name WHERE title='';


/* end portal */


INSERT IGNORE INTO api_table_view_type(id,name,solution_id) VALUES('LISTVIEW','View for listviews',1);
INSERT IGNORE INTO api_table_view_type(id,name,solution_id) VALUES('SELECTVIEW','View for comboboxes',1);


INSERT IGNORE INTO api_ui_app (id, name,description,home_url,solution_id)
VALUES (
1,'Default','System Verwaltungs App','/ui/v1.0/data/view/api_user/default?app_id=1',1);


INSERT IGNORE INTO api_ui_app_nav_item_type (id,solution_id, name) VALUES (1,1, 'Sidebar');
INSERT IGNORE INTO api_ui_app_nav_item_type (id,solution_id, name) VALUES (2,1, 'Navbar');


DELETE FROM api_ui_app_nav_item WHERE solution_id=1;

INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (100,1,'Benutzer','/ui/v1.0/data/view/api_user/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (105,1,'Sitzungen','/ui/v1.0/data/view/api_session/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (200,1,'Tabellen','/ui/v1.0/data/view/api_table/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (205,1,'Sichten','/ui/v1.0/data/view/api_table_view/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (210,1,'Daten Formatierungs Type','/ui/v1.0/data/view/api_data_formatter_type/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (220,1,'Daten Formatierungen','/ui/v1.0/data/view/api_data_formatter/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (230,1,'Felder','/ui/v1.0/data/view/api_table_field/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (390,1,'Portals Host','/ui/v1.0/data/view/api_portal_host/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (400,1,'Portale','/ui/v1.0/data/view/api_portal/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (410,1,'Portal Inhalts Typen','/ui/v1.0/data/view/api_portal_content_type/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (420,1,'Portal Inhalte','/ui/v1.0/data/view/api_portal_content/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (700,1,'Dateien','/ui/v1.0/data/view/api_file/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (900,1,'Einstellungen','/ui/v1.0/data/view/api_setting/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (1200,1,'Eventhandler','/ui/v1.0/data/view/api_event_handler/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (1300,1,'Process Log (nur Fehler)','/ui/v1.0/data/view/api_process_log/default',1,1);
INSERT IGNORE INTO api_ui_app_nav_item(id, app_id,name,url,type_id,solution_id) VALUES (1400,1,'Process Log (alle)','/ui/v1.0/data/view/api_process_log/all',1,1);



/*
End APP
*/

INSERT IGNORE INTO api_setting(setting,value,description,solution_id) VALUES ('portal.default_portal','default','Default portal_id',1);
INSERT IGNORE INTO api_setting(setting,value,description,solution_id) VALUES ('datalist.page_size','10','Page Size',1);


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
            <field name="disabled" table_alias="s" formatter="boolean"/>
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
        <field name="disabled" table_alias="u" formatter="boolean"/>
        <field name="is_admin" table_alias="u" formatter="boolean"/>
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
21,'LISTVIEW','default_old',12,'id',1,'<restapi type="select">
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
        <field name="is_active" table_alias="t" alias="Aktiviert"/>
        <field name="title" table_alias="t" alias="Titel"/>
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

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
34,'LISTVIEW','default',13,'id',1,'<restapi type="select">
    <table name="api_event_handler" alias="e"/>
    <filter type="or">
        <condition field="publisher" alias="e" value="$$query$$" operator="$$operator$$"/>
    </filter>
    <select>
        <field name="id" table_alias="e" alias="id"/>
        <field name="publisher" table_alias="e" alias="Publisher"/>
        <field name="event" table_alias="e" alias="Event"/>
        <field name="type" table_alias="e" alias="Type"/>
    </select>
</restapi>');


INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
35,'LISTVIEW','active',19,'id',1,'<restapi type="select">
    <table name="api_portal_content" alias="t"/>
    <filter type="and">
        <filter type="or">
            <condition field="name" alias="t" value="$$query$$" operator="$$operator$$"/>
            <condition field="name" alias="t" value="$$query$$" operator="$$operator$$"/>
        </filter>
        <condition field="is_active" alias="t" value="-1" operator="="/>
    </filter>
    <joins>
        <join type="inner" table="api_portal" alias="p" condition="t.portal_id=p.id"/>
    </joins>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="is_active" table_alias="t" alias="Aktiviert"/>
        <field name="title" table_alias="t" alias="Titel"/>
        <field name="name" table_alias="t" alias="Name"/>
        <field name="name" table_alias="p" alias="Portal"/>
    </select>
</restapi>');



INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
36,'LISTVIEW','default',23,'id',1,'<restapi type="select">
    <table name="api_process_log" alias="l"/>
    <filter type="and">
        <condition field="plugin_module_name" alias="e" value="$$query$$" operator="$$operator$$"/>
        <condition field="status_id" alias="l" value="10" operator="neq"/>
    </filter>
    <joins>
        <join type="inner" table="api_event_handler" alias="e" condition="l.event_handler_id=e.id"/>
        <join type="inner" table="api_process_log_status" alias="s" condition="l.status_id=s.id"/>
    </joins>
    <select>
        <field name="id" table_alias="l" alias="id"/>
        <field name="created_on" table_alias="l" alias="Created"/>
        <field name="name" table_alias="s" alias="Status"/>
        <field name="status_info" table_alias="l" alias="Info"/>
        <field name="error_text" table_alias="l" alias="Error"/>
        <field name="plugin_module_name" table_alias="e" alias="Module"/>
    </select>
    <orderby>
        <field name="created_on" alias="l" sort="DESC"/>
    </orderby>
</restapi>');



INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
37,'LISTVIEW','default',29,'id',1,'<restapi type="select">
    <table name="api_data_formatter_type" alias="t"/>
    <filter type="or">
        <condition field="name" alias="t" value="$$query$$" operator="$$operator$$"/>
    </filter>
    <select>
        <field name="id" table_alias="t" alias="id"/>
        <field name="name" table_alias="t" alias="Name"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
38,'LISTVIEW','default',30,'id',1,'<restapi type="select">
    <table name="api_data_formatter" alias="f"/>
    <filter type="or">
        <condition field="name" alias="f" value="$$query$$" operator="$$operator$$"/>
    </filter>
    <joins>
        <join type="left" table="api_table" alias="t" condition="f.table_id=t.id"/>
    </joins>
    <select>
        <field name="id" table_alias="f" alias="id"/>
        <field name="name" table_alias="f" alias="Name"/>
        <field name="alias" table_alias="t" alias="Tablename"/>
        <field name="type_id" table_alias="f" alias="Type"/>
    </select>
</restapi>');

INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
100,'LISTVIEW','all',23,'id',1,'<restapi type="select">
    <table name="api_process_log" alias="l"/>
    <filter type="and">
        <condition field="plugin_module_name" alias="e" value="$$query$$" operator="$$operator$$"/>
    </filter>
    <joins>
        <join type="inner" table="api_event_handler" alias="e" condition="l.event_handler_id=e.id"/>
        <join type="inner" table="api_process_log_status" alias="s" condition="l.status_id=s.id"/>
    </joins>
    <select>
        <field name="id" table_alias="l" alias="id"/>
        <field name="created_on" table_alias="l" alias="Created"/>
        <field name="name" table_alias="s" alias="Status"/>
        <field name="status_info" table_alias="l" alias="Info"/>
        <field name="error_text" table_alias="l" alias="Error"/>
        <field name="plugin_module_name" table_alias="e" alias="Module"/>
    </select>
    <orderby>
        <field name="created_on" alias="l" sort="DESC"/>
    </orderby>
</restapi>');




INSERT IGNORE INTO api_table_view (id,type_id,name,table_id,id_field_name,solution_id,fetch_xml) VALUES (
110,'LISTVIEW','default',12,'id',1,'<restapi type="select">
    <table name="api_table_view" alias="v"/>
    <orderby>
        <field name="table_id" alias="v" sort="DESC"/>
    </orderby>
</restapi>');


/* out_data_formatter */
INSERT IGNORE INTO api_data_formatter(id,name, table_id,type_id) VALUES (1,'$api_sub-table',7,2);

UPDATE api_data_formatter SET
name='$api_sub-table',
mime_type='text/html',
template_header='<div class="table-responsive">
<table class="table table-hover table-sm">
<thead>
<th>ID</th>
<th>User</th>
<th>Letzter Zugriff</th>
<th>Erstellt am</th>
</thead>
<tbody>
',
template_line='<tr onclick="url=\'/ui/v1.0/data/{{ table_meta[\'alias\'] }}/{{ data[table_meta[\'id_field_name\']] }}{{ build_query_string(context) }}\';alert(url); ">
<td>{{ data[\'id\'] }}</td>
<td>{{ data[\'user_id\'] }}</td>
<td>{{ data[\'last_access_on\'] }}</td>
<td>{{ data[\'created_on\'] }}</td>
</tr>',
template_footer='</tbody>
</table>
</div>'
WHERE id=1 AND provider_id='MANUFACTURER';

