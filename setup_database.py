from photo_sqlite import exec
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
exec('''

CREATE TABLE files (
    file_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT,
    filename    TEXT,
    album_id    INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT (DATETIME('now','localtime'))
)
''')

exec('''

CREATE TABLE albums(
    album_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    user_id     TEXT,
    created_at  TIMESTAMP DEFAULT (DATETIME('now','localtime'))
)
''')

print('ok')