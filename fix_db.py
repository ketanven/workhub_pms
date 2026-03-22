from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    cursor.execute("DROP TABLE IF EXISTS core_role_permissions;")
    cursor.execute("DROP TABLE IF EXISTS core_permission;")
    cursor.execute("DROP TABLE IF EXISTS core_role;")
    
    try:
        cursor.execute("ALTER TABLE core_admin DROP FOREIGN KEY core_admin_role_id_680da481_fk_core_role_id;")
    except: pass
    try:
        cursor.execute("ALTER TABLE core_admin DROP INDEX core_admin_role_id_680da481;")
    except: pass
    try:
        cursor.execute("ALTER TABLE core_admin DROP COLUMN role_id;")
    except: pass
    try:
        cursor.execute("ALTER TABLE core_admin ADD COLUMN role VARCHAR(20) DEFAULT 'sub_admin';")
    except: pass
    try:
        cursor.execute("DELETE FROM core_admintoken;")
        cursor.execute("DELETE FROM core_admin;")
    except: pass
    
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    print("DB fix applied v2.")
