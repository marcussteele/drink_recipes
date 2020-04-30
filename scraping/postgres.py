import psycopg2

def create_connection(db_config):
    conn = psycopg2.connect(
    host='localhost',
    port=db_config['port'],
    dbname=db_config['dbname'],
    user=db_config['user'])
    return conn

def create_database(database_name, connection):
    cur = connection.cursor()
    cur.execute(f"CREATE DATABASE {database_name};")
    cur.close()

def create_table(table_name, connection):
    cur = connection.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (name varchar PRIMARY KEY, recipe varchar, steps varchar, rating integer, description varchar);")
    cur.close()

def add_to_database(execute_str, connection):
    cur = connection.cursor()
    cur.execute(execute_str)
    cur.execute()
    connection.commit()
    cur.close()