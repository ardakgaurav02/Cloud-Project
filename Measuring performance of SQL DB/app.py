from unittest import skip
from flask import Flask, render_template, request, redirect, url_for, flash
import os
from os.path import join, dirname, realpath
import pandas as pd
import pymssql 
import numpy as np
from azure.storage.blob import BlobClient,generate_blob_sas, BlobSasPermissions,PublicAccess,BlobServiceClient
import urllib.request
from datetime import datetime, timedelta
from azure.storage.blob import generate_container_sas, ContainerSasPermissions  
from geopy.distance import geodesic
from numpy.ma import count
from time import time
import redis

r = redis.StrictRedis(host='GA-Redis.redis.cache.windows.net',
        port=6380, db=0, password='lGFTAbAH0JMB6XULyjsV8629d3vuPqlmZAzCaN5VLvk=', ssl=True)

app = Flask(__name__)
app.secret_key = "Hello there"

# enable debugging mode
app.config["DEBUG"] = True

# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

conn = pymssql.connect(
    server='g-server.database.windows.net',
    user='gca9216', 
    password='admin@02', 
    database='GA-Database')

cursor = conn.cursor()

account_name = "ardakstorage"
account_key = "TPbNjH0/wq+6d12wMKDl6rlA2+Ktzz+K+fgb4ky44xks6gHDKi9ExZtRAHDhMbse+Nxwmmhcdof8+ASteWZ+YQ=="
container_name = "ga-container"

def get_img_url_with_container_sas_token(blob_name):
    container_sas_token = generate_container_sas(
        account_name=account_name,
        container_name=container_name,
        account_key=account_key,
        permission=ContainerSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    blob_url_with_container_sas_token = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{container_sas_token}"
    return blob_url_with_container_sas_token

def get_img_url_with_blob_sas_token(blob_name):
    blob_sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=ContainerSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    blob_url_with_blob_sas_token = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{blob_sas_token}"
    return blob_url_with_blob_sas_token

#Root URL
@app.route('/')
def index():
    image = get_img_url_with_blob_sas_token("Arbor.png")
    blob_name=image
    return render_template('index.html', image=blob_name)

@app.route('/higestmag', methods=['POST', 'GET'])
def higestmag():
    name = None
    # start_time = None
    # stop_time = None
    final_time = None
    if  request.method == "POST":  
        user = request.form['user']  
        final_time, name =  cach(user)
    return render_template('higestmag.html', name=name, final_time=final_time)
def cach(user1):
    if r.exists(user1)==1:
        app.logger.info('if loop')
        j = 0
        start_time = time()
        while j <= 400:
            res = r.get(user1)
            name = eval(res)
            j = j+1
        stop_time = time()
        #name = eval(res)
        final_time = stop_time-start_time
        return final_time, name
    else:
        app.logger.info('else loop')
        #start_time = time()
        i = 0 
        start_time = time()
        while i <= 400:
            query_string = f"SELECT TOP {user1} * FROM earthquake ORDER BY mag DESC"
            cursor.execute(query_string, (user1))
            name = cursor.fetchall()
            i = i+1
        stop_time = time()
        #stop_time = time()
        final_time = stop_time-start_time
        #name = cursor.fetchall()
        r.set(user1,str(name))
        return final_time, name

@app.route('/magdate', methods=['POST', 'GET'])
def magdate():
    name = None
    final_time =None
    if  request.method == "POST":  
        user2 = request.form['user2']
        user3 = request.form['user3']
        final_time, name =  cach2(user2,user3)
    return render_template('/magdate.html', name=name, final_time=final_time )
def cach2(user2,user3):
    user = user2+user3
    if r.exists(user)==1:
        app.logger.info('if loop')
        j = 0
        start_time = time()
        while j <= 400:
            res = r.get(user)
            name = eval(res)
            j = j+1
        stop_time = time()
        #name = eval(res)
        final_time = stop_time-start_time
        return final_time, name
    else:
        app.logger.info('else loop')
        #start_time = time()
        i = 0 
        start_time = time()
        while i <= 400:
            query_string = f"select * from earthquake where mag > 1.0 AND times > '{user2}' AND times < '{user3}' "
            cursor.execute(query_string)
            name = cursor.fetchall()
            i = i+1
        stop_time = time()
        #stop_time = time()
        final_time = stop_time-start_time
        #name = cursor.fetchall()
        r.set(user,str(name))
        return final_time, name

@app.route('/uploadFiles', methods=['POST', 'GET'])
def uploadFiles():
      # get the uploaded file
    if request.method=="POST":
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            # set the file path
            uploaded_file.save(file_path)
            parseCSV(file_path)
            # save the file
        return redirect(url_for('uploadFiles'))
    return render_template('uploadFiles.html')

def newTable():
    sql1 = "DROP TABLE IF EXISTS data"
    cursor.execute(sql1)
    conn.commit()
    #time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource
    sql2 = "create table earthquake(times varchar(250), latitude varchar(250), longitude varchar(250), depth varchar(250), mag varchar(250),magtype varchar(250),nst varchar(250),gap varchar(250),dmin varchar(250),rms varchar(250),net varchar(250),id varchar(250),updated varchar(250),place varchar(250),type varchar(250),horizontalError varchar(250),depthError varchar(250),magError varchar(250), magNst varchar(250), status varchar(250), locationSource varchar(250), magSource varchar(250));"
    cursor.execute(sql2)
    conn.commit()
    
def parseCSV(filePath):
    if  filePath.endswith('.png'):
        path = 'static/files'
        file_names = os.listdir(path)
        account_name = 'ardakstorage'
        account_key = 'TPbNjH0/wq+6d12wMKDl6rlA2+Ktzz+K+fgb4ky44xks6gHDKi9ExZtRAHDhMbse+Nxwmmhcdof8+ASteWZ+YQ=='
        container_name = 'ga-container'
        connection_string = 'DefaultEndpointsProtocol=https;AccountName=ardakstorage;AccountKey=TPbNjH0/wq+6d12wMKDl6rlA2+Ktzz+K+fgb4ky44xks6gHDKi9ExZtRAHDhMbse+Nxwmmhcdof8+ASteWZ+YQ==;EndpointSuffix=core.windows.net'
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        for file_name in file_names:
            if file_name.endswith('.png'):
                blob_name = file_name
                file_path = path+'/'+file_name
                blob_client = container_client.get_blob_client(blob_name)
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(data, blob_type="BlockBlob", overwrite=True)  

    elif filePath.endswith('.csv'):
        newTable()
        # CVS Column Names
        col_names = ['times','latitude','longitude','depth','mag','magType','nst','gap','dmin','rms','net','id','updated','place','type','horizontalError','depthError','magError','magNst','status','locationSource','magSource']
        # Use Pandas to parse the CSV file
        csvData = pd.read_csv(filePath,names=col_names, header=None)
        csvData = csvData.replace(np.nan,None)
        # Loop through the Rows
        for i,row in csvData.iterrows():
            sql = "INSERT INTO earthquake (times, latitude, longitude, depth, mag, magType, nst,	gap, dmin, rms, net, id, updated, place, type, horizontalError, depthError, magError, magNst, status, locationSource, magSource) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            value = (row['times'],row['latitude'],row['longitude'],row['depth'],row['mag'],row['magType'],row['nst'],row['gap'],row['dmin'],row['rms'],row['net'],row['id'],row['updated'],row['place'],row['type'],row['horizontalError'],row['depthError'],row['magError'],row['magNst'],row['status'],row['locationSource'],row['magSource'])
            app.logger.info(sql%(value))
            cursor.execute(sql, value)
            conn.commit()
            
    else:
        skip
if (__name__ == "__main__"):
      app.run()


