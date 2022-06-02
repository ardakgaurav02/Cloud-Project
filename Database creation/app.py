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

app = Flask(__name__)
app.secret_key = "Hello there"

# enable debugging mode
app.config["DEBUG"] = True

# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

conn = pymssql.connect(
    server='a-server.database.windows.net',
    user='gaar', 
    password='admin@02', 
    database='GA-Database')

cursor = conn.cursor()

account_name = "sqlvan3strizzcvavo"
account_key = "IrDkhzurb5WszF7VweoOtF3sovFjqSiggTCef6jo+9VXCMCP8skGv+y/RytONzYAle2rHxijW9EgknZF+3GSWQ=="
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

@app.route('/adduser', methods=['POST', 'GET'])
def adduser():
    if 'submit_button' in request.form:
        Name = request.form['name']
        State = request.form['state']
        Salary = request.form['salary']
        Grade = request.form['grade']
        Room = request.form['room']
        TelNum = request.form['telnum']
        Picture = request.form['picture']
        Keywords = request.form['keywords']
        query_string = "INSERT INTO people (Names, States, Salary, Grade, Room, Telnum, Picture, Keywords)  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query_string, (Name, State, Salary, Grade, Room, TelNum, Picture, Keywords))
        conn.commit()
    return render_template('adduser.html')

@app.route('/update', methods=['POST', 'GET'])
def update():
    user = None
    for k in request.form.items():
        app.logger.info(k)
    if  request.method == "POST":
        query_string = "select * from people where Names = %s"
        if 'submit_button' in request.form:
            updateuser()
            user = request.form['name']
        else:
            user = request.form['user']
            
        
        cursor.execute(query_string, (user))
        #conn.commit()
        user = cursor.fetchall()
        #return redirect(url_for('update'))
    return render_template('update.html', user=user)

def updateuser():
    
        Name = request.form['name']
        State = request.form['state']
        Salary = request.form['salary']
        Grade = request.form['grade']
        Room = request.form['room']
        TelNum = request.form['telnum']
        Keywords = request.form['keywords']
        cursor.execute("""
            UPDATE people
            SET Names = %s,
                States = %s,
                Salary = %s,
                Grade = %s,
                Room = %s,
                Telnum = %s,
                Keywords = %s
            WHERE Names = %s
        """, (Name, State, Salary, Grade, Room, TelNum, Keywords, Name))
        #flash('Employee Updated Successfully')
        conn.commit()


@app.route('/grtfilter', methods=['POST', 'GET'])
def grtfilter():
    name = None
    blob_name=None
    if  request.method == "POST":  
        user = request.form['user']  
        query_string = "SELECT Names FROM people WHERE Salary > %s"
        cursor.execute(query_string, (user))
        name = cursor.fetchall()
        blob_name = []
        for images in name:
            image = images[0]+'.png'
            image = get_img_url_with_blob_sas_token(image)
            blob_name.append(image)
            app.logger.info(image)
    return render_template('grtfilter.html', image=blob_name)

@app.route('/lessfilter', methods=['POST', 'GET'])
def lessfilter():
    name = None
    blob_name=None
    if  request.method == "POST":  
        user = request.form['user']  
        query_string = "SELECT Names FROM people WHERE Salary < %s"
        cursor.execute(query_string, (user))
        name = cursor.fetchall()
        blob_name = []
        for images in name:
            image = images[0]+'.png'
            image = get_img_url_with_blob_sas_token(image)
            blob_name.append(image)
            app.logger.info(image)
    return render_template('lessfilter.html', image=blob_name)

@app.route('/all')
def all():
    query_string = "SELECT * FROM people"
    cursor.execute(query_string)
    name = cursor.fetchall()
    return render_template('all.html', name=name )

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    query_string = "SELECT * FROM people"
    cursor.execute(query_string)
    name = cursor.fetchall()
    if  request.method == "POST":
       username()
       cursor.execute(query_string)
       name = cursor.fetchall()
    return render_template('delete.html', name=name )

def username():
    if  request.method == "POST":
        user = request.form['user']
        query_string = "DELETE FROM people WHERE Names = %s"
        cursor.execute(query_string, (user))
        conn.commit()
        #user = cursor.fetchall()
        flash('User Deleted successfully!')
        
        #return redirect(url_for('delete'))
    #return render_template('delete.html')

@app.route('/search', methods=['POST', 'GET'])
def search():
    picture=None
    blob_name=None
    if  request.method == "POST":
        user = request.form['user']
        query_string = "SELECT names FROM people WHERE Names = %s"
        cursor.execute(query_string, (user))
        user = cursor.fetchall()
        picture = user[0][0]
        for images in picture:
            images = (picture+'.png')
            images = get_img_url_with_blob_sas_token(images)
            blob_name=images
            app.logger.info(images)
    return render_template('search.html',user=picture, images=blob_name)

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
        account_name = 'sqlvan3strizzcvavo'
        account_key = 'IrDkhzurb5WszF7VweoOtF3sovFjqSiggTCef6jo+9VXCMCP8skGv+y/RytONzYAle2rHxijW9EgknZF+3GSWQ=='
        container_name = 'ga-container'
        connection_string = 'DefaultEndpointsProtocol=https;AccountName=sqlvan3strizzcvavo;AccountKey=IrDkhzurb5WszF7VweoOtF3sovFjqSiggTCef6jo+9VXCMCP8skGv+y/RytONzYAle2rHxijW9EgknZF+3GSWQ==;EndpointSuffix=core.windows.net'
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
        col_names = ['Names','States','Salary','Grade','Room','Telnum','Picture','Keywords']
        # Use Pandas to parse the CSV file
        csvData = pd.read_csv(filePath,names=col_names, header=None)
        csvData = csvData.replace(np.nan,None)
        # Loop through the Rows
        for i,row in csvData.iterrows():
            sql = "INSERT INTO people (Names, States, Salary, Grade, Room, Telnum, Picture, Keywords) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            value = (row['Names'],row['States'],row['Salary'],row['Grade'],row['Room'],row['Telnum'],row['Picture'],row['Keywords'])
            app.logger.info(sql%(value))
            cursor.execute(sql, value)
            conn.commit()
            
    else:
        skip

if (__name__ == "__main__"):
     app.run()

