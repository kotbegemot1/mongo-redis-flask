import ast
import os
from flask_caching import Cache
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')

app.config["MONGO_URI"] = f"mongodb://{MONGO_HOST}:27017/flask"
app.config['MONGO_DBNAME'] = 'dashboard' 

mongo = PyMongo(app)
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:6379/0'})


@app.route('/msg', methods=['POST'])
@cache.cached()
def message():
    data = request.args
    if request.method == 'POST':
        if data.get('text'):
            res = mongo.db.dashboard.insert_one(dict(data))
            return jsonify({'ok': True, 'message': f'Message{res.inserted_id}'}), 200
        else:
            return jsonify({'ok': False, 'message': 'Text not found'}), 400
        
        
@app.route('/tag/<ObjectId:message_id>', methods=['POST'])
@cache.cached()
def add_tag_to_message(message_id):
    data = request.args
    if request.method == 'POST':
        if data.get('text'):
            res = mongo.db.dashboard.update_one({"_id": message_id}, {"$addToSet": {"tags": dict(data)}})
            return jsonify({'ok': True, 'message': f'Tag inserted successfully {res}'}), 200
        else:
            return jsonify({'ok': False, 'message': 'Text should present'}), 400

@app.route('/comment/<ObjectId:message_id>', methods=['POST'])
@cache.cached()
def add_comment_to_message(message_id):
    data = request.args
    if request.method == 'POST':
        if data.get('text'):
            res = mongo.db.dashboard.update_one({"_id": message_id}, {"$add": {"comments": dict(data)}})
            return jsonify({'ok': True, 'message': 'Comment inserted successfully % s ' % res}), 200
        else:
            return jsonify({'ok': False, 'message': 'Text should present'}), 400


@app.route('/msg/<ObjectId:message_id>', methods=['GET'])
@cache.cached()
def message_by_id(message_id):
    if request.method == 'GET':
            res = mongo.db.dashboard.find_one_or_404(message_id)
            return jsonify({'ok': True, 'message': 'Message found  % s ' % res}), 200

@app.route('/stats/<ObjectId:message_id>', methods=['GET'])
@cache.cached()
def stats_by_id(message_id):
    if request.method == 'GET':
        res = mongo.db.dashboard.find_one_or_404(message_id)
        tags = 0 
        comments = 0 
        if 'tags' in res.keys():
            tags =  len(ast.literal_eval(res['tags']))
        if 'comments' in res.keys():
            comments = len(ast.literal_eval(res['comments']))
        return jsonify({'ok': True, 'message': f'Message has {tags} tags and {comments} comments'}), 200



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)