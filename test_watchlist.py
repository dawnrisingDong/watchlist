import unittest

from watchlist import app,db
from watchlist.models import Movie,User
from watchlist.commands import forge,initdb


ctx = app.app_context()
ctx.push()

"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
app.config['TESTING'] = True    #关闭对模型修改的监控"""

class WatchlistTestCase(unittest.TestCase):     # 测试用例

    def setUp(self):
        #更新配置
        app.config.update(
            TESTING = True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'    # 使用内存型数据库
        )  
        db.create_all()

        user = User(name='Test',username='test')
        user.set_password('123')
        movie = Movie(title='Test movie title',year='2023')
        db.session.add_all([user,movie])    # 一次添加多个模型类实例
        db.session.commit()

        self.client = app.test_client() # 创建测试客户端
        self.runner = app.test_cli_runner() # 创建测试命令运行器

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于运行状态
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])



    # 测试404页面
    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)  # 设置true返回数据文本形式
        self.assertIn('Page Not Found - 404',data)
        self.assertIn('Go Back',data)
        self.assertEqual(response.status_code,404)


    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist',data)
        self.assertIn('Test movie title',data)
        self.assertEqual(response.status_code,200)

    # 辅助方法登录账户
    def login(self):
        self.client.post('/login',data=dict(
            username = 'test',
            password = '123'
        ),follow_redirects=True)

    
    # 测试创建
    def test_create_item(self):
        self.login()

        response = self.client.post('/',data=dict(
            title = 'New movie',
            year = '2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created!',data)
        self.assertIn('New movie',data)
        
        response = self.client.post('/',data=dict(
            title = '',
            year = '2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input!',data)
        self.assertNotIn('Item created!',data)

        response = self.client.post('/',data=dict(
            title = 'New1',
            year = ''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input!',data)
        self.assertNotIn('Item created!',data)


    # 测试更新
    def test_update_item(self):
        self.login()
        # 测试页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item',data)
        self.assertIn('Test movie title',data)
        self.assertIn('2023',data)

        # 测试操作
        response = self.client.post('/movie/edit/1',data=dict(
            title = 'New movie Edited',
            year = '2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item update.',data)
        self.assertIn('New movie Edited',data)

        response = self.client.post('/movie/edit/1', data=dict(
            title = '',
            year = '2023'
        ) , follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input!',data)
        self.assertNotIn('Item update.',data)

        response = self.client.post('/movie/edit/1', data=dict(
            title = 'New movie Edited Again',
            year = ''
        ) , follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input!',data)
        self.assertNotIn('Item update.',data)
        self.assertNotIn('New movie Edited Again',data)


    # 测试删除
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted!',data)
        self.assertNotIn('Test movie title',data)
        

    # 测试登录
    def test_login(self):
        response = self.client.post('/login',data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.',data)
        self.assertIn('Logout',data)
        self.assertIn('Settings',data)
        self.assertIn('Delete',data)
        self.assertIn('Edit',data)
        self.assertIn('<form method="post">',data)

        response = self.client.post('/login',data=dict(
            username='test',
            password='111'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.',data)
        self.assertIn('Invalid username or password!',data)

        response = self.client.post('/login',data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.',data)
        self.assertIn('Invalid username or password!',data)

        response = self.client.post('/login',data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.',data)
        self.assertIn('Invalid input!',data)

        response = self.client.post('/login',data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.',data)
        self.assertIn('Invalid input!',data)

    # 测试登出
    def test_logout(self):
        self.login()
        
        response = self.client.get('/logout',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Bye bye ~',data)
        self.assertNotIn('Logout',data)
        self.assertNotIn('Settings',data)
        self.assertNotIn('Delete',data)
        self.assertNotIn('Edit',data)
        self.assertNotIn('<form method="post">',data)


    # 测试设置
    def test_settings(self):
        self.login()
        # 测试页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings',data)
        self.assertIn('Your Name',data)

        response = self.client.post('/settings',data =dict(
            name = 'New name'
        ) , follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Setting updated!',data)
        self.assertIn('New name',data)

        response = self.client.post('/settings',data =dict(
            name = ''
        ) , follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Setting updated!',data)
        self.assertIn('Invalid input!',data)


# 测试命令

    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done.',result.output)
        self.assertNotEqual(Movie.query.count(),0)

    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialize the database.',result.output)

    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin','--username','dawn_r1sing','--password','123'])
        self.assertIn('Done.',result.output)
        self.assertIn('Creating user...',result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username,'dawn_r1sing')
        self.assertTrue(User.query.first().validate_password('123'))

    def test_admin_update_command(self):
        result = self.runner.invoke(args=['admin','--username','new_name','--password','456'])
        self.assertIn('Done.',result.output)
        self.assertIn('Updating user...',result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username,'new_name')
        self.assertTrue(User.query.first().validate_password('456'))


if __name__ == '__main__':
    unittest.main()
        










    
