import sqlite3

USER_LOGIN_LIST = {
    'taro': 'aaa',
    'jiro': 'bbb',
    'sabu': 'ccc',
    'siro': 'ddd',
    'goro': 'eee',
    '8': 'fff' }

conn = sqlite3.connect('chattest.db')
c = conn.cursor()

for k,v in USER_LOGIN_LIST.items():
    c.execute("insert into user values(null,?,?)",(k,v))
    
conn.commit()
c.close()