from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages  
import requests
from subprocess import run,PIPE
import os
from os.path import isfile
import sys
from django.views.generic import TemplateView
from wsinterfaceproject.functions.functions import handle_uploaded_file
from .forms import ProfileForm 
from django.core.files.storage import FileSystemStorage

import numpy as np
import cv2
import os
import sys
import shutil
import glob
from os import listdir
import math
import logging
from azure.storage.blob import BlockBlobService
from azure.storage.queue import QueueService, QueueMessageFormat
from PIL import Image
from io import BytesIO
from datetime import datetime


def extractFrames(pathOut,filepath):
    print('Extracting frames')

    # Path to video file 
    cap = cv2.VideoCapture(filepath) 
    print(cap, isfile(filepath))
    print(filepath)
    #Reducing the frames per second of the video to 2
    cap.set(cv2.CAP_PROP_FPS, 0.2)   
    # Used as counter variable 
    x=1
    frameRate = cap.get(5) #frame rate
    numberOfPicturesPerSecond= 0.1 #0.2
    blockBlobService = BlockBlobService(account_name='storageworkersafety', account_key='oLyRX3ZuRBztBddfYyJktlV3AM+InU2VcvuX9poY94dlbZFqBW5gdVDyrWQUorwXhyV2Bi3LbTSps4enm++4KA==')
    #blockBlobService2 = BlockBlobService(account_name='wssafedistancing', account_key='JMM7MecLzmnnPF+nK/THdfaE69RpvcNGtmQ782vulU9c4945uBX2y5s8QyWptvNv7cjgDTKf61tfvohsHZ7wXA==')

    # start creating frames from video

    
    while(cap.isOpened()):
        print('Getting the frame')
        frameId = cap.get(1) #current frame number
        ret, frame = cap.read()
        if (ret != True):
            break

        # in case frame matches a multiple of the frame, create image
        if frameId  % math.floor(frameRate/numberOfPicturesPerSecond) == 0:
            logging.info("create cap" + str(x))
            # convert frame to PIL image
            frame_conv = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            pilImage = Image.fromarray(frame_conv)
            #Calculate size = Height/2 * Width/2
            size = (round(pilImage.size[0]/2), round(pilImage.size[1]/2))
            #Resize using CV2
            #pilImage = pilImage.resize(size, Image.ANTIALIAS)
            imgByteArr = BytesIO()
            pilImage.save(imgByteArr, format='jpeg')
            #print(type(pilImage))          
            imgByteArr = imgByteArr.getvalue()
            imageDecode = cv2.imencode('.jpg',frame)[1].tobytes()
            # write image to blob for logging
            now = datetime.strftime(datetime.now(), "%Y%m%dT%H%M%S%Z")
            imageFileName= 'image' +  str(int(x)) + "_img_" + now + ".jpg"
            #imageFileName= 'folder' + "/log/image" +  str(int(x)) + "_img.png"
            queueclient = QueueService(account_name='storageworkersafety', account_key='oLyRX3ZuRBztBddfYyJktlV3AM+InU2VcvuX9poY94dlbZFqBW5gdVDyrWQUorwXhyV2Bi3LbTSps4enm++4KA==',endpoint_suffix='core.windows.net')
            blockBlobService.create_blob_from_bytes('camera-feed', imageFileName, imageDecode)
            #blockBlobService.create_blob_from_bytes('videoblob\epm_stage', imageFileName, imageDecode)
            queueclient.encode_function = QueueMessageFormat.text_base64encode
            queueclient.decode_function = QueueMessageFormat.text_base64decode
            #imageFile = unicode(s, "utf-8")
            queueclient.put_message('camera-feed',imageFileName)
            print('written to queue' , imageFileName)
            #blockBlobService2.create_blob_from_bytes('videoblob', imageFileName, imgByteArr)
            #Write to local directory
            pilImage.save(os.path.join(pathOut , "image{:d}".format(x))+now+".jpg")
            #cv2.imwrite(os.path.join(pathOut , "image{:d}.jpeg".format(x)),frame)
         # increment ima
            x+=1
            
def uploadtoblob(filepath):
    block_blob_service = BlockBlobService(account_name='storageworkersafety', account_key='oLyRX3ZuRBztBddfYyJktlV3AM+InU2VcvuX9poY94dlbZFqBW5gdVDyrWQUorwXhyV2Bi3LbTSps4enm++4KA==')
    container_name ='camera-feed'

    #local_path = "D:\\Test\\test"

    for files in os.listdir(filepath):
        block_blob_service.create_blob_from_path(container_name,files,os.path.join(filepath,files),timeout=1000)   

# Create your views here.

def button(request):
    return render(request , 'home.html')

def home(request):
    return render(request , 'home.html')

def EPMFileUpload(request):
    return render(request, "EPMFileUpload.html")
   
def IncidentReport(request):
    return render(request,'IncidentManagementReport.html')
    
def SupervisorReport(request):
    return render(request,'SupervisorReport.HTML')

def output(request):
    data = requests.get("https://reqres.in/api/users")    
    print(data.text)
    data = data.text
    return render(request , 'home.html' , {'data' : data})

def external(request):
    inp = request.POST.get('fileupload')
    filename = 'BreakSingleVideotoFrames.py'
    path = os.getcwd()+'\\'+filename
    print(path)
    if isfile(filename):
        print('Yup exists',type(filename))
    if isfile(path):
        print('Yup path exists', type(path))
    
    #run([sys.executable , filename, inp] ,shell=False ,stdout = PIPE) 
    media_path = './media/'
    frame_generated_path = './FramesGenerated/'
    list_of_files = glob.glob('./media/*.mp4') # * means all if need specific format then *.csv
    print(list_of_files)
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    extractFrames(frame_generated_path , latest_file )
    #for file_name in listdir(media_path):
    #        #print(os.path.join('/media', file_name))
    #       file = os.path.join(media_path, file_name)
    #        #file = media_path+file_name
    #        print(file)
            
    #        extractFrames(frame_generated_path , file )
   #uploadtoblob('./FramesGenerated')
   # out = "file submitted Successfully"
    return render(request , 'EPMFileUpload.html' )

def upload_file(request):  
    if request.method == 'POST': 
        uploaded_file = request.FILES['fileupload']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
        #print(uploaded_file.name)
        #print(uploaded_file.size)
        #profile = ProfileForm(request.POST, request.FILES)  
        #if profile.is_valid():  
        #    handle_uploaded_file(request.FILES['fileupload'])  
    #return HttpResponse("File uploaded successfuly") 
        media_path = './media/'
        frame_generated_path = './FramesGenerated/'
        list_of_files = glob.glob('./media/*.mp4') # * means all if need specific format then *.csv
        print(list_of_files)
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)
        extractFrames(frame_generated_path , latest_file )
        messages.info(request, 'File has been uploaded and is being analyzed.')
        return render(request,'EPMFileUpload.html')
        return HttpResponse("File uploaded successfuly")

    else:  
    #    profile = ProfileForm()  
    #    return HttpResponse("Fuck") 
         print("nada")
        #return render(request,"EPMFileUpload.html",{'form':Profile})  
