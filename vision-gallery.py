from bottle import route,run, static_file
import sqlite3
import os

@route('/static/<filename:path>')
def server_static(filename):
    root_path = os.path.join(os.path.dirname(__file__), 'static')
    return static_file(filename, root=root_path)

#Class For Interacting with Database
#path() is used for using database in same folder as script
class database:
    def path():
        current_directory = os.path.dirname(os.path.abspath(__file__))
        db_name = 'image.db'
        file_path = os.path.join(current_directory, db_name)

        return file_path

    def db_create():
        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        create_table = '''
                            create table if not exists image_table(
                                id integer primary key,
                                image_name text,
                                caption text,
                                tag text,
                                description text
                            )
                        '''

        cursor.execute(create_table)
        conn.commit()
        conn.close()

    def db_select():
        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        sql = 'select * from image_table order by id desc'
        cursor.execute(sql)
        record = cursor.fetchall()
        conn.commit()
        conn.close()

        return record

    def db_insert(image, query):

        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        sql = 'insert into image_table(image_name, caption, tag, description) values(?,?,?,?)'
        #query[0] = Caption , query[1] = Tags , query[2] = Description
        cursor.execute(sql,(image, query[0], query[1], query[2]))
        conn.commit()
        conn.close()
  
#Index Page.
@route('/')
def index():
    record = database.db_select()

    page=''
    for x in record:
        image_path = f'./static/{x[1]}'

        page =  f'''
                    {page} 
                    <hr>
                    <div style="display:flex;">
                        <div>
                            <img style="width:400px; height:auto;" src="{image_path}">
                        </div>
                        <div>
                            <strong>{x[2]}</strong>
                            <hr>
                            {x[3]}
                            <hr>
                            {x[4]}
                        </div>    
                    </div>
                '''


    return page

database.db_create()

run(host='0.0.0.0', port=80, debug=True)