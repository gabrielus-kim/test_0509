from flask import Flask

app = Flask(__name__,
            static_folder='static',
            template_folder='template')

app.config['ENV']='development'
app.config['DEBUG']=True

@app.route('/')
def index():

    return 'WELCOM PYTHON'

app.run(port=8000)