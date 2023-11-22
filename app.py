import os
import click

from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy #导入扩展类

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    #关闭对模型修改的监控
#在扩展类实例化之前加载配置
db = SQLAlchemy(app)    #初始化扩展，传入程序实例app

#@app.route('/')
#def hello():
#    return '<h1>Welcome to My Watchlist!</h1><img src="https://raw.githubusercontent.com/dawnrisingDong/pic_bed/main/img/202311211734885.gif">'

#创建模型类来表示这两张表（用户信息+电影条目信息）
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    #实例化db.Column、主键
    name = db.Column(db.String(20)) #名字

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True) # 主键
    title = db.Column(db.String(60))    #标题
    year = db.Column(db.String(4))      #年份

@app.cli.command()  #注册为命令，可以传入name参数来自定义命令
@click.option('--drop',is_flag=True,help='Create after drop.')  #设置选项
def initdb(drop):       #默认函数名就是命令的名字
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialize the database.')  #输出提示信息


@app.route('/')
def index():
    user = User.query.first()   #读取用户记录
    movies = Movie.query.all()  #读取所有电影
    return render_template('index.html',user=user ,movies=movies)

@app.cli.command()
def forge():
    """Generate fake data."""
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
