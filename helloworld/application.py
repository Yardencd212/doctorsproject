#!flask/bin/python
import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
import requests
import boto3
from flask_cors import CORS

application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})

@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/get_doctors', methods=['GET'])
def get_id():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('doctors')
    # replace table scan ###
    resp = table.scan()
    print(str(resp))
    return Response(json.dumps(str(resp['Items'])), mimetype='application/json', status=200)
    
# curl -i -X POST -d'{"name":"Shiran", "department":"Surgery", "years":"20"}' -H "Content-Type: application/json" http://localhost:5000/set_doctor/4
@application.route('/set_doctor/<id>', methods=['POST'])
def set_doc(id):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('doctors')
    # get post data  
    data = request.data
    # convert the json to dictionary
    data_dict = json.loads(data)
    # retreive the parameters
    name = data_dict.get('name','default')
    department = data_dict.get('department','defualt')
    years = data_dict.get('years', 'default')

    item={
    'id': id,
    'name': name,
    'department': department, 
    'years': years 
     }
    table.put_item(Item=item)
    
    return Response(json.dumps(item), mimetype='application/json', status=200)


if __name__ == '__main__':
    flaskrun(application)
