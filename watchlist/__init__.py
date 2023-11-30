import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy #导入扩展类
from flask_login import LoginManager


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','dev') 
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path),os.getenv('DATABASE_FILE','data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    #关闭对模型修改的监控


db = SQLAlchemy(app)    #初始化扩展，传入程序实例app
login_manager = LoginManager(app)   #实例化扩展



#模板上下文处理函数
@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)


@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    user = User.query.get(int(user_id))
    return user

login_manager.login_view = 'login'


from watchlist import commands,views,errors