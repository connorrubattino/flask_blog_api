from app import app

# Define a route
@app.route("/")
def index():
    first_name = 'Connor'
    age = 25
    return 'Hello ' + first_name + ' who is ' + str(age) + ' years old'

@app.route('/test')
def test():
    my_dicts = []
    for i in range(5):
        a_dict = {
            'id': i+1,
            'key': 'value',
            'name': 'Connor'
        }
        my_dicts.append(a_dict)
        
    return my_dicts