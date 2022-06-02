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
#from PIL import Image
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

@app.route('/maxEQ', methods=['POST', 'GET'])
def maxEQ():
    starting = None
    lat1 = None
    long1 = None
    
    magnitude1 = []
    finalresult1 = []

    lat2 = None
    long2 = None
    magnitude2 = []
    finalresult2 = []
    if  request.method == "POST":  
        lat1 = request.form['lat1']
        long1 = request.form['long1']
        destination1 = (lat1, long1)

        lat2 = request.form['lat2']
        long2 = request.form['long2']
        destination2 = (lat2, long2)

        query_string = f"SELECT latitude, longitude, place, mag FROM data"
        cursor.execute(query_string)
        starting = cursor.fetchall()

        for n in starting:
            dist1 = geodesic(destination1, n[:2]).kilometers
            if dist1<1000:
                #result.append((n[0],n[1],n[2],n[3],dist))
                magnitude1.append((n[3]))
            finalresult1 = count(magnitude1)
        app.logger.info(finalresult1)
        # for m in result:
        #     if m[3] == mag:
        #         finalresult.append((m[0],m[1],m[2],m[3],m[4]))

        for m in starting:
            dist2 = geodesic(destination2, m[:2]).kilometers
            if dist2<1000:
                #result.append((n[0],n[1],n[2],n[3],dist))
                magnitude2.append((m[3]))
            finalresult2 = count(magnitude2)
        app.logger.info(finalresult2)
        # for m in result:
        #     if m[3] == mag:
        #         finalresult.append((m[0],m[1],m[2],m[3],m[4]))

        if finalresult1 > finalresult2:
            flash("Destination1 has maximum earthquake")
        elif finalresult1 == finalresult2:
            flash("Both have same number of earthquake")
        else:
            flash("Destination2 has maximum earthquake")   
    return render_template('maxEQ.html')

@app.route('/magdate', methods=['POST', 'GET'])
def magdate():
    starting = None
    lat = None
    long = None
    result = []
    magnitude = []
    finalresult = []
    mag = None
    if  request.method == "POST":  
        lat = request.form['lat']
        long = request.form['long']
        destination = (lat, long)
        query_string = f"SELECT latitude, longitude, place, mag FROM data"
        cursor.execute(query_string)
        starting = cursor.fetchall()
        app.logger.info(starting[1:2])
        for n in starting:
            dist = geodesic(destination, n[:2]).kilometers
            if dist<500:
                result.append((n[0],n[1],n[2],n[3],dist))
                magnitude.append((n[3]))
        mag = max(magnitude)
        for m in result:
            if m[3] == mag:
                finalresult.append((m[0],m[1],m[2],m[3],m[4]))
    return render_template('magdate.html', name=finalresult)

@app.route('/higestmag', methods=['POST', 'GET'])
def higestmag():
    name = None
    if  request.method == "POST":  
        user = request.form['user']  
        query_string = f"SELECT TOP {user} * FROM data ORDER BY mag DESC"
        cursor.execute(query_string, (user))
        name = cursor.fetchall()
    return render_template('higestmag.html', name=name )

# @app.route('/magdate', methods=['POST', 'GET'])
# def magdate():
#     name = None
#     if  request.method == "POST":  
#         user1 = request.form['user1']
#         user2 = request.form['user2']
#         user3 = request.form['user3']
#         query_string = f"select count(*) from data where mag > '{user1}' AND time > '{user2}' AND time < '{user3}' "
#         cursor.execute(query_string, (user1,user2,user3))
#         name = cursor.fetchall()
#     return render_template('/magdate.html', name=name )

@app.route('/recentdata', methods=['POST', 'GET'])
def recentdata():
    name = None
    if  request.method == "POST":  
        user1 = request.form['user1']
        user2 = request.form['user2']
        query_string = f"select count(mag) as range1 from data where updated > '2022-02-09' AND updated < '2022-02-12' AND (mag > '{user1}' and mag <= '{user2}')"
        cursor.execute(query_string, (user1,user2))
        name = cursor.fetchall()
    return render_template('/recentdata.html', name=name )

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
        # CVS Column Names
        col_names = ['time','latitude','longitude','depth','mag','magType','nst','gap','dmin','rms','net','id','updated','place','type','horizontalError','depthError','magError','magNst','status','locationSource','magSource']
        # Use Pandas to parse the CSV file
        csvData = pd.read_csv(filePath,names=col_names, header=None)
        csvData = csvData.replace(np.nan,None)
        # Loop through the Rows
        for i,row in csvData.iterrows():
            sql = "INSERT INTO data (time, latitude, longitude, depth, mag, magType, nst,	gap, dmin, rms, net, id, updated, place, type, horizontalError, depthError, magError, magNst, status, locationSource, magSource) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            value = (row['time'],row['latitude'],row['longitude'],row['depth'],row['mag'],row['magType'],row['nst'],row['gap'],row['dmin'],row['rms'],row['net'],row['id'],row['updated'],row['place'],row['type'],row['horizontalError'],row['depthError'],row['magError'],row['magNst'],row['status'],row['locationSource'],row['magSource'])
            #app.logger.info(sql%(value))
            cursor.execute(sql, value)
            conn.commit()
            
    else:
        skip
if (__name__ == "__main__"):
     app.run()

