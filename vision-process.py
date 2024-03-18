from openai import OpenAI
import sqlite3
import os
import base64
import requests

#OpenAI Settings
api_key = "APIKEY"
client = OpenAI(api_key=api_key)

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

#Encode Image in base64
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#Upload and Process Image
def image_process(image_path):
    image_query = ['provide a caption for this image in fewer than 10 words',
                    'provide 10 tags for this image in CSV format',
                    'provide a description for this image']

    base64_image = encode_image(image_path)

    response_list =[]
    for query in image_query:
    # Getting the base64 string

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
                ]
            }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response = response.json()
        response = response['choices'][0]['message']['content']
        response_list.append(response)

    return response_list

#Create Database if does not exist
database.db_create()

# ADD NEW IMAGES TO DATABASE
current_directory = os.path.dirname(os.path.abspath(__file__))

image_list = os.listdir(f'{current_directory}/static/')

#Processes and Adds Image to Database if No Record Exists Yet
#Set to only recognize png files, ad "or" to if statement to add additional image types
for image in image_list:
    if 'png' in image:
        image_path = os.path.join(f'{current_directory}/static/', image)

        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        sql = f"select * from image_table where image_name = '{image}'"
        cursor.execute(sql)
        record = cursor.fetchall()
        conn.commit()
        conn.close()

        if not record:
            response = image_process(image_path)
            database.db_insert(image, response)
            print(f'Added {image}\n{response}')
        else:
            print('Already in Database')