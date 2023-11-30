from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from watchlist import db


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



