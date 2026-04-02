import sqlite3

conn = sqlite3.connect("base.db")
cursor = conn.cursor()
new_user = True

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
                username char,
                password char
               )
""")

print("hello")
print("put your username")
username = input()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

def loging():
    global new_user
    for i in rows:
        if i[0] == username:
            print("put your password")
            password = input()
            if i[1] == password:
                new_user = False
                print("welcome back")
                break
            else:
                print("please try again")
                loging()

loging()

if new_user == True:
    print("create your password")
    password = input()
    cursor.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
    print("your account was created")
    conn.commit()

conn.close()
