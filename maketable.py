import sqlite3
conn = sqlite3.connect('chattest.db')
c = conn.cursor()
c.execute(
    "create table user(id integer primary key autoincrement,name text,password text)"
)
c.execute(
    "create table chat(id integer primary key autoincrement, user_id1 integer, user_id2 integer, room text)"
)
c.execute(
    "create table chatmess(id integer primary key autoincrement, chat_id integer, to_user integer, from_user integer, message text)"
)
# c.execute("select * from user")
# list1 = c.fetchone()
# print(list1)

