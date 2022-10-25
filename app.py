from flask import Flask, redirect, request, session
from flask import render_template, send_file
from flask import request, Markup
import photo_db, sns_user as user
import sns_user as user, sns_data as data
import os, time
import pdb
import sqlite3

app = Flask(__name__)
app.secret_key = 'dpwvgAxaY2iWHMb2'

@app.route('/login')
def login():
    return render_template('login_form.html')

@app.route('/login/try',methods=['POST'])
def login_try():
    ok = user.try_login(request.form)
    if not ok: return msg('ログイン失敗')
    return redirect('/')

@app.route('/logout')
def logout():
    user.try_logout()
    return msg('ログアウトしました')

@app.route('/')
@user.login_required
def index():
    me = user.get_id()
    return render_template('index.html',id=me,photos=photo_db.get_files(),
            users=user.get_allusers(),
            fav_users=data.get_fav_list(me),
            timelines=data.get_timelines(me))

@app.route('/album/<album_id>')
@user.login_required
def album_show(album_id):
    album = photo_db.get_album(album_id)
    return render_template('album.html',album=album,photos=photo_db.get_album_files(album_id))

@app.route('/user/<user_id>')
@user.login_required
def user_page(user_id):
    return render_template('user.html',id=user_id,photos=photo_db.get_user_files(user_id))

@app.route('/users/<user_id>')
def users(user_id):
    if user_id not in user.USER_LOGIN_LIST:
        return msg('ユーザーが存在しません')
    me = user.get_id()
    return render_template('users.html',
            user_id=user_id, id=me,
            is_fav=data.is_fav(me, user_id),
            text_list=data.get_text(user_id))

@app.route('/upload')
@user.login_required
def upload():
    return render_template('upload_form.html',albums=photo_db.get_albums(user.get_id()))

@app.route('/upload/try', methods=['POST'])
@user.login_required
def upload_try():
    upfile = request.files.get('upfile',None)
    if upfile is None: return msg('アップロード失敗')
    if upfile.filename == '': return msg('アップロード失敗')
    album_id = int(request.form.get('album','0'))
    
    photo_id = photo_db.save_file(user.get_id(), upfile, album_id)
    if photo_id == 0: return msg('データベースのエラー')
    return redirect('/user/' + str(user.get_id()))

@app.route('/album/new')
@user.login_required
def album_new():
    return render_template('album_new_form.html')

@app.route('/album/new/try')
@user.login_required
def album_new_try():
    id = photo_db.album_new(user.get_id(), request.args)
    if id == 0: return msg('新規アルバム作成に失敗')
    return redirect('/upload')

@app.route('/write')
@user.login_required
def write():
    return render_template('write_form.html',
            id=user.get_id())

@app.route('/write/try', methods=['POST'])
@user.login_required
def try_write():
    text = request.form.get('text', '')
    if text == '': return msg('テキストが空です。')
    data.write_text(user.get_id(), text)
    return redirect('/')

@app.route('/photo/<file_id>')
@user.login_required
def photo(file_id):
    ptype = request.args.get('t','')
    photo = photo_db.get_file(file_id,ptype)
    if photo is None: return msg('ファイルがありません')
    return send_file(photo['path'])

def msg(s):
    return render_template('msg.html', msg=s)

@app.route("/userlist")
def userlist():
    conn = sqlite3.connect('chattest.db')
    c = conn.cursor()
    c.execute("select id, name from user")
    user_info = c.fetchall()
    conn.close()
    
    return render_template("userlist.html", tpl_user_info=user_info)

@app.route("/chatroom/<int:other_id>", methods=["POST"])
def chatroom_post(other_id):
    if "user_id" in session:#http://192.168.1.27:5000/chatroom/None
        # まずはチャットルームがあるかchatidをとってくる
        my_id = session["user_id"]
        print(my_id)
        conn = sqlite3.connect('chattest.db')
        c = conn.cursor()
        c.execute(
            "select id from chat where (user_id1 = ? and user_id2 = ?) or (user_id1 = ? and user_id2 = ?)", (my_id, other_id, other_id, my_id))
        chat_id = c.fetchone()

        print(chat_id)
        # とってきたidの中身で判定。idがNoneであれば作成、それ以外(数字が入っていれば)スルー
        if chat_id == None:

            c.execute("select name from user where id = ?", (my_id,))
            myname = c.fetchone()[0]
            c.execute("select name from user where id = ?", (other_id,))
            othername = c.fetchone()[0]
            # ルーム名を作る
            room = myname + "と" + othername + "のチャット"
            c.execute("insert into chat values(null,?,?,?)",
                      (my_id, other_id, room))
            conn.commit()
            # 作ったチャットルームのidを取得
            c.execute(
                "select id from chat where (user_id1 = ? and user_id2 = ?) or (user_id1 = ? and user_id2 = ?)", (my_id, other_id, other_id, my_id))
            chat_id = c.fetchone()
        conn.close()
        print(chat_id)
        return redirect("/chat/{}".format(chat_id[0]))
    else:
        return redirect("/login")

@app.route("/chatroom")
def chatroom_get():
    if "user_id" in session:
        my_id = session["user_id"]
        conn = sqlite3.connect('chattest.db')
        c = conn.cursor()
        # ここにチャットルーム一覧をDBからとって、表示するプログラム
        c.execute(
            "select id, room from chat where user_id1 = ? or user_id2 = ?", (my_id, my_id))
        chat_list = c.fetchall()
        
        return render_template("/chatroom.html", tpl_chat_list=chat_list)
    else:
        return redirect("/login")

@app.route("/chat/<string:chatid>")
def chat_get(chatid):
    if "user_id" in session:
        my_id = session["user_id"]
        # ここにチャットをDBからとって、表示するプログラム
        conn = sqlite3.connect('chattest.db')
        c = conn.cursor()
        c.execute(
            "select chatmess.to_user, chatmess.from_user, chatmess.message, user.name from chatmess inner join user on chatmess.from_user = user.id where chat_id = ?", (chatid,))
        chat_fetch = c.fetchall()
        chat_info = []
        for chat in chat_fetch:
            chat_info.append(
                {"to": chat[0], "from": chat[1], "message": chat[2], "fromname": chat[3]})
        c.execute("select room from chat where id = ?", (chatid,))
        room_name = c.fetchone()[0]
        c.close()
        return render_template("chat.html", chat_list=chat_info, link_chatid=chatid, tpl_room_name=room_name, tpl_my_id=my_id)
    else:
        return redirect("/login")


@app.context_processor
def add_staticfile():
    return dict(staticfile=staticfile_cp)
def staticfile_cp(fname):
    import os
    path = os.path.join(app.root_path, 'static', fname)
    mtime = str(int(os.stat(path).st_mtime))
    return '/static/' + fname + '?v=' + str(mtime)

@app.template_filter('linebreak')
def linebreak_filter(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;') \
        .replace('>', '&gt;').replace('\n', '<br>')
    return Markup(s)

@app.template_filter('datestr')
def datestr_filter(s):
    return time.strftime('%Y年%m月%d日 ',
    time.localtime(s))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

