import web
import psycopg2
import pymssql
import sys


urls = (
    '/', 'Index',
    '/home', 'Home',
    '/select', 'SelectDb',
    '/delete/(.*)', 'DeleteDb',
    '/create', 'CreateDb',
)


def _get_db_obj():
    from settings import DATABASES
    for i in DATABASES:
        port = DATABASES[i]['PORT']
        username = DATABASES[i]['USER']
        password = DATABASES[i]['PASSWORD']
        host = DATABASES[i]['HOST']
        db_name = DATABASES[i]['NAME']
        db = DATABASES[i]['ENGINE']
        if 'mysql' in db:
            _ = Postgresql('mysql', db_name, username, password, host, port)
        elif 'postgresql' in db:
            _ = Postgresql('postgresql', db_name, username, password, host, port)
        return _


class Index:
    def GET(self):
        return '''
<form method="post" action="/">
Please input "settings.py" file path: <input type="text" name="settings">
<input type="submit" value="input">
</form>'''

    def POST(self):
        data = web.input()
        try:
            path = data['settings']
            sys.path.append(path)
            from settings import DATABASES
        except Exception as e:
            sys.path.pop(-1)
            return e
        return web.redirect('/home')


class Home:
    def GET(self):
        print(sys.path)
        db_obj = _get_db_obj()
        result = db_obj.select_()
        db_obj.close_()
        value = ''
        for i in result:
            if i:
                default_return = '<p>%s</p>'
                value += default_return % i[0]
        def_value = '''
<form method="post" action="/home">
choice action(create/delete)?
<select name="do">
<option value="delete">delete</option>
<option value="create">create</option>
</select>
</br> 
Please input db name
<input type="text" name="dbName">
<input type="submit" value="input">
</form>
'''
        return value + def_value

    def POST(self):
        print(sys.path)
        data = web.input()
        print('收到post数据', data['dbName'], data['do'])
        db_obj = _get_db_obj()
        try:
            if data['do'] == 'create':
                db_obj.create_(db_name=data['dbName'])
            elif data['do'] == 'delete':
                db_obj.delete_(db_name=data['dbName'])
        except Exception as e:
            db_obj.close_()
            return "<p>%s</p>" % e
        return web.redirect('/home')


class SelectDb:
    def GET(self):
        db_obj = _get_db_obj()
        result = db_obj.select_()
        db_obj.close_()
        value = ''
        for i in result:
            if i:
                default_return = '<p>%s</p>'
                value += default_return % i[0]
        return value


class CreateDb:
    def GET(self):
        value = '''
<form method="post" action="/create">
Please input db name</br> <input type="text" name="dbName">
<input type="submit" value="input">
</form>
'''
        return value

    def POST(self):
        data = web.input()
        db_obj = _get_db_obj()
        try:
            db_obj.create_(data['dbName'])
        except Exception as e:
            db_obj.close_()
            return '<p>%s</p>' % e
        else:
            db_obj.close_()
        return web.redirect('/select')


class DeleteDb:
    def GET(self, db_name):
        db_obj = _get_db_obj()
        try:
            db_obj.delete_(db_name)
        except Exception as e:
            db_obj.close_()
            return e
        else:
            db_obj.close_()
            return 'ok'


class Postgresql:
    createDB_sql = "CREATE DATABASE {db};"
    postgresql_showDB_sql = 'SELECT datname FROM pg_database;'
    mysql_showDB_sql = 'SHOW DATABASES;'
    deleteDB_sql = 'DROP DATABASE {db};'
    def __init__(self, db_type, db, us, pa, ho, po=None):
        self.db_type = db_type
        if self.db_type == 'mysql':
            self.conn = pymssql.connect(
                database=db,
                user=us,
                password=pa,
                host=ho,
                port=po
            )
        elif self.db_type == 'postgresql':
            self.conn = psycopg2.connect(
                database=db,
                user=us,
                password=pa,
                host=ho,
                port=po
            )
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.conn.cursor()

    def create_(self, db_name, sql=createDB_sql):
        sql = sql.format(db=db_name)
        self.cur.execute(sql)

    def select_(self):
        if self.db_type == 'mysql':
            sql = self.mysql_showDB_sql
        elif self.db_type == 'postgresql':
            sql = self.postgresql_showDB_sql
        self.cur.execute(sql)
        value = self.cur.fetchall()
        return value

    def delete_(self, db_name, sql=deleteDB_sql):
        sql = sql.format(db=db_name)
        self.cur.execute(sql)

    def commit_(self):
        self.conn.commit()

    def close_(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()