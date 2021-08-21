#!flask/bin/python
import json
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
import requests
import boto3
from flask_cors import CORS
import datetime
from datetime import datetime


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
    return Response(json.dumps(resp['Items']), mimetype='application/json', status=200)
    
# curl -i http://"localhost:5000/set_doctor?id=8&name=Dor&department=finance&years=13"
@application.route('/set_doctor', methods=['GET'])
def set_doc():
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('doctors')
    did = request.args.get('id')
    name = request.args.get('name')
    department = request.args.get('department')
    years = request.args.get('years')
    item={
    'id': did,
    'name': name,
    'department': department, 
    'years': years 
     }
    table.put_item(Item=item)
    
    return Response(json.dumps(item), mimetype='application/json', status=200)

#curl -i http://"localhost:5000/del_doctor?id=1"
@application.route('/del_doctor' , methods=['GET'])

def del_doc():
    id=request.args.get('id')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('doctors')
    
    resp = table.delete_item(
        Key={
            'id':id
        }
        )
    print (str(resp))
    return Response(json.dumps(str(resp)), mimetype='application/json', status=200)

#curl localhost:8000/analyze/doctorspictures/stato.jpg 

@application.route('/analyze/<bucket>/<image>', methods=['GET'])
def analyze(bucket='doctorspictures', image='stato.jpg'):
    return detect_labels(bucket, image)
def detect_labels(bucket, key, max_labels=3, min_confidence=90, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    s3 = boto3.resource('s3', region_name = 'us-east-1')
    image = s3.Object(bucket, key) # Get an Image from S3
    img_data = image.get()['Body'].read() # Read the image
    response = rekognition.detect_labels(
        Image={
            'Bytes': img_data
        },
        MaxLabels=max_labels,
		MinConfidence=min_confidence,
    )
    return json.dumps(response['Labels'])
    


#curl localhost:8000/comp_face/doc1.jpg/doc2.jpg

@application.route('/comp_face/<source_image>/<target_image>', methods=['GET'])
def compare_face(source_image, target_image):
    # change region and bucket accordingly
    region = 'us-east-1'
    bucket_name = 'doctorspictures'
	
    rekognition = boto3.client("rekognition", region)
    response = rekognition.compare_faces(
        SourceImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name":source_image,
    		}
    	},
    	TargetImage={
    		"S3Object": {
    			"Bucket": bucket_name,
    			"Name": target_image,
    		}
    	},
		# play with the minimum level of similarity
        SimilarityThreshold=50,
    )
    # return 0 if below similarity threshold
    return json.dumps(response['FaceMatches'] if response['FaceMatches'] != [] else [{"Similarity": 0.0}])
  
  
@application.route('/upload_image' , methods=['POST'])
def uploadImage():
    mybucket = 'doctorspictures'
    filobject = request.files['img']
    s3 = boto3.resource('s3', region_name='us-east-1')
    date_time = datetime.now()
    dt_string = date_time.strftime("%d-%m-%Y-%H-%M-%S")
    filename = "%s.jpg" % dt_string
    s3.Bucket(mybucket).upload_fileobj(filobject, filename, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
    imageUrl='https://doctorspictures.s3.amazonaws.com/%s'%filename
    return {"imageUrl": imageUrl}

if __name__ == '__main__':
    flaskrun(application)
