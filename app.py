from flask import Flask, render_template, request , jsonify
import logging 
logging.basicConfig(filename='log.log', level=logging.DEBUG, 
                    format='%(asctime)s:%(levelname)s:%(message)s')


app = Flask(__name__)

@app.route('/')
def index():
    tab3_string='this string is coming from flask backend ! '
    title = 'My Website'
    content1 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed eget eros et lectus bibendum dictum. Quisque eget lorem vestibulum, lobortis dolor ac, suscipit odio. Aliquam bibendum velit sapien, sed lobortis augue lobortis a.'
    content2 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed eget eros et lectus bibendum dictum. Quisque eget lorem vestibulum, lobortis dolor ac, suscipit odio. Aliquam bibendum velit sapien, sed lobortis augue lobortis a.'
    services = ['Service 1', 'Service 2', 'Service 3']
    footer_text = 'Copyright © 2023 My Website'
    return render_template('home.html', title=title, content1=content1, content2=content2, services=services, footer_text=footer_text,tab3_string=tab3_string)


@app.route('/update-item', methods=['POST'])
def update_item():
    item = request.form.get('item')
    checked = request.form.get('checked')
    # Do something with the item and checked value
    # ...
    print(item)
    print(checked)
    checkbox_state = request.form.getlist('todo-list')
    print(checkbox_state)
    return jsonify({'status': 'success'})


@app.route('/checklist', methods=['POST'])
def checklist():
    data = request.json
    name = data['name']
    isChecked = data['isChecked']
    print(f'{name} is checked: {isChecked}')
    logging.log(logging.INFO, 'This is a custom debug message')
    logging.log(logging.INFO, F'{name} : {isChecked}')
    
    return jsonify({'message': 'Success'})

if __name__=='__main__':
    app.run(debug=True)