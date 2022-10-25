from tinydb import TinyDB, Query
import time, os

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = BASE_DIR + '/data/data.json'

db = TinyDB(DATA_FILE)

def get_fav_table():
    return db.table('fav'),Query()

def add_fav(id, fav_id):
    table, q = get_fav_table()
    a = table.search(
        (q.id == id) & (q.fav_id == fav_id))
    if len(a) == 0:
        table.insert({'id': id, 'fav_id': fav_id})

def is_fav(id, fav_id):
    table, q = get_fav_table()
    a = table.get(
        (q.id == id) & (q.fav_id == fav_id))
    return a is not None

def remove_fav(id, fav_id):
    table, q = get_fav_table()
    table.remove(
        (q.id == id ) & (q.fav_id == fav_id))

def get_fav_list(id):
    table, q = get_fav_table()
    a = table.search(q.id == id)
    return [row['fav_id'] for row in a]

def get_text_table():
    return db.table('text'), Query()

def write_text(id, text):
    table, q = get_text_table()
    table.insert({
        'id': id,
        'text': text,
        'time': time.time()})

def get_text(id):
    table,q = get_text_table()
    return table.search(q.id == id)

def get_timelines(id):

    table,q = get_text_table()
    favs = get_fav_list(id)
    favs.append(id)

    tm = time.time() - (24*60*60) * 30
    a = table.search(
        q.id.one_of(favs) & (q.time > tm))

    return sorted(a,
            key=lambda v:v['time'],
            reverse=True)