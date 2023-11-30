from watchlist import app,db
from watchlist.models import User,Movie

from flask import request,flash,redirect,url_for,render_template
from flask_login import current_user,login_user,logout_user,login_required


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


#编辑
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


#删除
@app.route('/movie/delete/<int:movie_id>',methods=['GET','POST'])
@login_required #登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted!')
    return redirect(url_for('index'))


#设置
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





