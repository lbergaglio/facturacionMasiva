import psycopg2

#print(psycopg2.drivers())

conn = psycopg2.connect(
            host="cpl-saez-varmsbi01",
            database="abms",
            user="sa_arms_consultas",
            password="GS4n99rZZsBnXzFLbzyDc"
)

print("✅ Conexión exitosa:", conn)
conn.close()
