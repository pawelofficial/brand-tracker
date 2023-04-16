from flask import Flask, render_template, request , jsonify
import logging 
logging.basicConfig(filename='./logs/flask.log', level=logging.DEBUG, 
                    format='%(asctime)s:%(levelname)s:%(message)s')


class myclass:
    def __init__(self) -> None:
        self.channels={'item1':None,'item2':None,'item3':None}
    
    
    



app = Flask(__name__)
c=myclass()

@app.route('/')
def index():
    tab3_string='this string is coming from flask backend ! '
    title = 'My Website'
    content1 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed eget eros et lectus bibendum dictum. Quisque eget lorem vestibulum, lobortis dolor ac, suscipit odio. Aliquam bibendum velit sapien, sed lobortis augue lobortis a.'
    content2 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed eget eros et lectus bibendum dictum. Quisque eget lorem vestibulum, lobortis dolor ac, suscipit odio. Aliquam bibendum velit sapien, sed lobortis augue lobortis a.'
    services = ['Service 1', 'Service 2', 'Service 3']
    footer_text = 'Copyright © 2023 My Website'
    return render_template('home.html', title=title, content1=content1, content2=content2, services=services, footer_text=footer_text,tab3_string=tab3_string)


@app.route('/checklist', methods=['POST'])
def checklist():
    data = request.json
    name = data['name']
    isChecked = data['isChecked']
    c.channels[name]=isChecked
    print(name, isChecked)
    logging.log(logging.INFO, f'c channels : {c.channels}')
    return jsonify({'message': 'Success'})

if __name__=='__main__':
    app.run(debug=True)