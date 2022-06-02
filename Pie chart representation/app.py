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

# Root URL
@app.route('/')
def index():
    image = get_img_url_with_blob_sas_token("Arbor.png")
    blob_name=image
    return render_template('index.html', image=blob_name)

@app.route('/higestmag', methods=['POST', 'GET'])
def higestmag():
    data = [('Task','My task')]
    if  request.method == "POST":  
        user = request.form['user1']
        # user2 = request.form['user2']      
        query_string = f"SELECT TOP {user} place, mag FROM earthquake ORDER BY mag DESC"   
        cursor.execute(query_string,(user))
        data += cursor.fetchall()
    app.logger.info(data)
    return render_template('higestmag.html', data=data )

@app.route('/recentdata', methods=['POST', 'GET'])
def recentdata():
    name = []
    ans = []
    if  request.method == "POST":  
        user1 = request.form['user1']
        user2 = request.form['user2']
        for i in range(int(user1), int(user2)):
            query_string = f"select count(mag) as [number of occurences] \
                from earthquake t\
                where t.mag between {i} and {i+1}"   
            cursor.execute(query_string)
            name = cursor.fetchall()
            ans.append((str(i)+'-'+str(i+1), name))
        app.logger.info(ans)
    return render_template('/recentdata.html', ans=ans)

#Google charts range pie chart
@app.route('/piechart', methods=['POST', 'GET'])
def piechart():
    name = []
    if  request.method == "POST":  
        user1 = request.form['user1']
        user2 = request.form['user2']
        name = [('Task','My task')]
        for i in range(int(user1), int(user2)):
            query_string = f"select count(mag) as [number of occurences] \
                from earthquake t\
                where t.mag between {i} and {i+1}"   
            cursor.execute(query_string)
            temp = cursor.fetchone()
            name.append((str(i)+'-'+str(i+1), temp[0]))
    app.logger.info(name)
    return render_template('piechart.html', name=name)

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
    sql1 = "DROP TABLE IF EXISTS earthquake"
    cursor.execute(sql1)
    conn.commit()
    #time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource
    sql2 = "create table earthquake(time varchar(25), latitude varchar(25), longitude varchar(25), depth varchar(25), mag varchar(25),magtype varchar(25),nst varchar(25),gap varchar(25),dmin varchar(25),rms varchar(25),net varchar(25),id varchar(25),updated varchar(25),place varchar(150),type varchar(25),horizontalError varchar(25),depthError varchar(25),magError varchar(25), magNst varchar(25), status varchar(25), locationSource varchar(25), magSource varchar(25));"
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
        col_names = ['time','latitude','longitude','depth','mag','magType','nst','gap','dmin','rms','net','id','updated','place','type','horizontalError','depthError','magError','magNst','status','locationSource','magSource']
        # Use Pandas to parse the CSV file
        csvData = pd.read_csv(filePath,names=col_names, header=None)
        csvData = csvData.replace(np.nan,None)
        # Loop through the Rows
        for i,row in csvData.iterrows():
            sql = "INSERT INTO earthquake (time, latitude, longitude, depth, mag, magType, nst,	gap, dmin, rms, net, id, updated, place, type, horizontalError, depthError, magError, magNst, status, locationSource, magSource) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            value = (row['time'],row['latitude'],row['longitude'],row['depth'],row['mag'],row['magType'],row['nst'],row['gap'],row['dmin'],row['rms'],row['net'],row['id'],row['updated'],row['place'],row['type'],row['horizontalError'],row['depthError'],row['magError'],row['magNst'],row['status'],row['locationSource'],row['magSource'])
            app.logger.info(sql%(value))
            cursor.execute(sql, value)
            conn.commit()    
    else:
        skip
        
if (__name__ == "__main__"):
      app.run()