from flask import Flask, render_template
from flask import request, session, redirect
import pymysql
from datetime import datetime

app = Flask(__name__,
            static_folder='static',
            template_folder='template')

db=pymysql.connect(
    user='root',
    passwd='avante',
    host='localhost',
    db='web',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

app.config['ENV']='development'
app.config['DEBUG']=True
app.secret_key='who are you?'

def who():
    if 'owner' in session:
        who='Owner : '+session['owner']['name']
    else:
        who='login ~ please.'
    return who

def do_I_join(user):
        cur=db.cursor()
        cur.execute(f"""
            select id, name, password from author
            where name='{user}'
        """)
        user=cur.fetchone()
        return user

def get_menu():
    menu=[]
    cur=db.cursor()
    cur.execute(f"""
        select id, title from topic
    """)
    menu_list=cur.fetchall()
    for row in menu_list:
        menu.append(f"""
        <li><a href='/{row['id']}'>{row['title']}</a></li>
        """)
    return '\n'.join(menu)

@app.route('/')
def index():
    content = '안녕하세요?'
    
    return render_template('template.html',
                        who=who(),
                        menu=get_menu(),
                        content=content)

@app.route('/<id>')
def search(id):
    if 'owner' in session:
        cur=db.cursor()
        cur.execute(f"""
            select id, title, description from topic
                where id='{id}'
        """)
        data=cur.fetchone()
        content=data['description']
    else:
        content='로그인을 해주세요 ~'
    return render_template('template.html',
                            who=who(),
                            id=id,
                            menu=get_menu(),
                            content=content)

@app.route('/register', methods=['GET','POST'])
def register():
    if 'owner' in session:
        if request.method == 'POST':
            cur=db.cursor()
            cur.execute(f"""
                insert into topic (title, description, created, author_id)
                    values ('{request.form['title']}',
                            '{request.form['desc']}',
                            '{datetime.now()}',
                            '{session['owner']['id']}')
            """)
            db.commit()
            return redirect('/')
        else:
             content='Topic 을 등록해 주세요 ~'
    else:
        content='Login 을 하셔야 Topic 을 등록하실 수 있읍니다.'
    return render_template('register.html',
                            who=who(),
                            menu=get_menu(),
                            content=content
                            )

@app.route('/delete/<id>')
def delete(id):
    if 'owner' in session:   
        cur=db.cursor()
        cur.execute(f"""
            delete from topic where id='{id}'
        """)
        db.commit()
    return redirect('/')

@app.route('/login', methods=['GET','POST'])
def login():
    content='로그인을 해주세요 ~'
    if 'owner' in session:
        content='로그인 상태 입니다.'
        return render_template('template.html',
                who=who(),
                content=content)

    if request.method == 'POST':
        user=do_I_join(request.form['id'])
        if user is None:
            content='로그인 아이디가 없읍니다.'
        else:
            cur=db.cursor()
            cur.execute(f"""
                select id, name, password from author
                where name='{request.form['id']}' 
                    and password=SHA2('{request.form['pw']}',256)
            """)
            user=cur.fetchone()
            if user is None:
                content='패스워드가 틀립니다.'
            else:
                session['owner']=user
                return redirect('/')
    return render_template('login.html',
                            who=who(),
                            menu=get_menu(),
                            content=content)

@app.route('/logout')
def logout():
    session.pop('owner',None)
    return redirect('/')

@app.route('/join', methods=['GET','POST'])
def join():
    content='회원 가입해 주세요.'
    if request.method == 'POST':
        user=do_I_join(request.form['id'])
        if user is None:
            cur=db.cursor()
            cur.execute(f"""
                insert into author (name, profile, password)
                    values ('{request.form['id']}',
                        '{request.form['pf']}',
                        SHA2('{request.form['pw']}',256))
            """)
            db.commit()
            return redirect('/')
        else:
            content='이미 가입된 login ID 입니다.'
    return render_template('join.html',
                            who=who(),
                            content=content)

@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    content='정말 회원탈퇴하실라구요?'
    if request.method == 'POST':
        user=do_I_join(request.form['id'])
        if user is None:
            content='가입 등록이 안된 ID 입니다. 확인 부탁드립니다.'
        else:
            cur=db.cursor()
            cur.execute(f"""
                delete from author where name='{request.form['id']}'
            """)
            db.commit()
            return redirect('/')
    return render_template('withdraw.html',
                            who=who(),
                            content=content)

app.run(port=8000)