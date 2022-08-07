import psycopg2

# conn = psycopg2.connect(database='organization',
#                         host='db.engr.msstate.edu',
#                         user='app_inventory',
#                         password='An)KW9?Sh-o3',
#                         port='5432')

conn = psycopg2.connect(database='benmoore',
                        host='localhost',
                        user='benmoore',
                        password='',
                        port='5432')

cursor = conn.cursor()

cursor.execute('SELECT * FROM inventory')
print(cursor.fetchone())