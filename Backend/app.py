import psycopg2
from dotenv import load_dotenv
import  os

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host
)
if conn:
    print("✅ Veritabanına başarıyla bağlanıldı!")
else:
    print("❌ Veritabanına bağlanılamadı.")
#cursor = conn.cursor()

username=input("Kullanıcı adınızı girin: ")
password=input("Şifrenizi girin: ")
cursor = conn.cursor()
cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password))
conn.commit()
print("✅ Kullanıcı başarıyla oluşturuldu!")