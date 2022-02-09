from distutils.core import setup
from logging import debug
from flask import Flask, json, request, jsonify, abort,render_template

from models import setup_db, Greeting
from flask_cors import CORS
from auth import test_import, requires_auth
from dotenv import load_dotenv
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# make sure you create a database named hello in psql

Page_count=2
def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__,template_folder='../templates')
    database_name = "hello"
    username=os.getenv("PSQL_USER")
    password=os.getenv("PSQL_PASSWORD")
    database_path = 'postgresql://{}:{}@localhost:5432/{}'.format(username,password,
        database_name)
    
    
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    # print("username ", username)
    # print("password ", password)
    setup_db(app,database_path)
    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    cors = CORS(app, resources={"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
                            'Access-Control-Allow-Headers',
                            'Content-Type,Authorization,true'
                            )
        response.headers.add(
                            'Access-Control-Allow-Methods',
                            'GET,PATCH,POST,DELETE,OPTIONS'
                            )
        return response
    # example greetings
    greetings = {
        'en': 'hello',
        'es': 'Hola',
        'ar': 'مرحبا',
        'ru': 'Привет',
        'fi': 'Hei',
        'he': 'שלום',
        'ja': 'こんにちは'
    }


    @app.route('/', methods=['GET'])
    def index():
        return "<h1>hello friends</h1>"


    @app.route('/greetings', methods=['GET'])
    @requires_auth(["get:greetings"])
    def greeting_all(payload):
        test_import()
        page = request.args.get('page',1, type=int)
        pagination = Greeting.query.paginate(page, per_page=Page_count,error_out=False)
        greetings = pagination.items
        # TODO implement pagination
        # greetings = Greeting.query.all()
        greetings = [greeting.format() for greeting in greetings]
        return jsonify({'greetings': greetings, 'count':pagination.total})



    @app.route('/greetings/<lang>', methods=['GET'])
    @requires_auth(["get:greetings"])
    def greeting_one(payload,lang):
        greeting = Greeting.query.filter_by(lang = lang).first()
        print(lang)
        # if(lang not in greetings):
        if(not greeting):
            abort(404)
        return jsonify({'greeting': greeting.format()})


    @app.route('/greetings', methods=['POST'])
    @requires_auth(["post:greetings"])
    def greeting_add(payload):
        info = request.get_json()
        if('lang' not in info or 'greeting' not in info):
            abort(422)
        # greetings[info['lang']] = info['greeting']
        greeting = Greeting(info['lang'], info['greeting'])
        greeting.insert()
        return jsonify({'greeting': greeting.format()}),201
    
    #TODO: implement beautifull greeting
    @app.route('/greetings/<lang>/beautiful', methods=['POST'])
    def beautiful_greeting(lang):
        greeting = "namastai"
        return jsonify({'greeting': f'greeting in language {lang} is {greeting}'})
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error": 422,
        }), 422
    @app.errorhandler(404)
    def unprocessable(error):
        return jsonify({
        "message":"resource not found",
        "success": False, 
        "error": 404,
        }), 404
    @app.errorhandler(401)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error": 401,
        }), 401
    
    @app.errorhandler(403)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error": 403,
        }), 403
    # if __name__ == "__main__":
    #     app.run(debug=True)

    @app.route('/hello')
    @limiter.limit('1 per day')
    def hello_world():
        return render_template("index.html")
                               
    return app
