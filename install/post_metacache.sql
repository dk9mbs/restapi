UPDATE api_table_field SET field_name=name WHERE field_name IS NULL;

ALTER TABLE api_activity DROP FOREIGN KEY IF EXISTS foreign_reference_api_activity_sprint_id_to_api_sprint;
ALTER TABLE api_activity DROP COLUMN IF EXISTS sprint_id;
DROP TABLE IF EXISTS api_activity_sprint;
DROP TABLE IF EXISTS api_activity_sprint_status;


DELETE IGNORE FROM api_table_field WHERE table_id=44 AND name='sprint_id';
DELETE IGNORE FROM api_table_field WHERE table_id IN (48,49);
DELETE IGNORE FROM api_table WHERE id IN (48,49) AND name='Sprint';
DELETE IGNORE FROM api_table WHERE id IN (48) AND alias='api_activity_sprint_status';
DELETE IGNORE FROM api_ui_app_nav_item WHERE id=4040 AND name='Sprint';

ALTER TABLE api_event_handler DROP COLUMN IF EXISTS plugin_module_type_id;
DROP TABLE IF EXISTS api_event_handler_module_type;
DELETE FROM api_table_field WHERE table_id=50;
DELETE FROM api_table WHERE id=50 AND name='Plugin typen' AND alias='api_event_handler_module_type';
DELETE FROM api_table_field WHERE label='plugin_module_type_id' AND name='plugin_module_type_id' AND table_id=9 AND type_id='int';


