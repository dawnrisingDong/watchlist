import os
import click
import os.path
import sys

from flask import Flask,render_template
from flask import request,url_for,flash,redirect
from flask_sqlalchemy import SQLAlchemy #导入扩展类
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from flask_login import login_user,login_required,logout_user,current_user
from flask_login import LoginManager

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(BASE_DIR,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    #关闭对模型修改的监控



#在扩展类实例化之前加载配置
db = SQLAlchemy(app)    #初始化扩展，传入程序实例app

app.config['SECRET_KEY'] = 'dev'

#@app.route('/')
#def hello():
#    return '<h1>Welcome to My Watchlist!</h1><img src="https://raw.githubusercontent.com/dawnrisingDong/pic_bed/main/img/202311211734885.gif">'

#创建模型类来表示这两张表（用户信息+电影条目信息）
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)    #实例化db.Column、主键
    name = db.Column(db.String(20)) #名字
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True) # 主键
    title = db.Column(db.String(60))    #标题
    year = db.Column(db.String(4))      #年份


#注册命令：注册用户
@app.cli.command()
@click.option('--username',prompt=True,help='The username used to login.')
@click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True,help='The password used to login.')
def admin(username,password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password) #设置密码
    else :
        click.echo('Creating user...')
        user = User(username=username,name='dawn_r1sing')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')

#用户加载回调函数
login_manager = LoginManager(app)   #实例化扩展
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user

#登录
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input!')
            return redirect(url_for('login'))
        
        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        
        flash('Invalid username or password!')
        return redirect(url_for('login'))
        
    return render_template('login.html')


#登出
@app.route('/logout')
@login_required
def logout():
    logout_user()   #登出用户
    flash('Bye bye ~')
    return redirect(url_for('index'))


#注册命令：初始化数据库
@app.cli.command()  
@click.option('--drop',is_flag=True,help='Create after drop.')  #设置选项
def initdb(drop):       #默认函数名就是命令的名字
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialize the database.')  #输出提示信息


#模板上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


#错误处理函数
@app.errorhandler(404)
def page_not_found(e):  #接受异常对象作为参数
    return render_template('404.html'),404  #返回模板和状态码（其他渲染默认状态码为200）


#主页视图函数
@app.route('/',methods=['GET','POST'])
def index():
    # 创建条目(不同于修改，创建条目和主页共用一个页面)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        
        title = request.form.get('title')
        year = request.form.get('year')

        #验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input!')
            return redirect(url_for('index'))
        
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created!')
        return redirect(url_for('index'))
    
    movies = Movie.query.all()  #读取所有电影
    return render_template('index.html' ,movies=movies)


#添加数据命令
@app.cli.command()
def forge():
    
    db.create_all()

    name = 'dawn_r1sing'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')



@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
@login_required #登录保护
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input!')
            return redirect(url_for('index'))
        
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item update.')
        return redirect(url_for('index'))
    
    return render_template('edit.html',movie = movie)


@app.route('/movie/delete/<int:movie_id>',methods=['GET','POST'])
@login_required #登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted!')
    return redirect(url_for('index'))


@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input!')
            return redirect(url_for('settings'))
        
        current_user.name = name    #返回当前登录用户的数据库记录对象
        db.session.commit()
        flash('Setting updated!')
        return redirect(url_for('index'))


    return render_template('settings.html')



