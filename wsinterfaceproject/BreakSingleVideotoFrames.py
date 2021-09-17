#!/usr/bin/python
# -*- coding: utf-8 -*-
# organize imports

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
from PIL import Image
from io import BytesIO
from datetime import datetime


def extractFrames(pathOut,filepath):

    # Path to video file 
    cap = cv2.VideoCapture(filepath) 
    #Reducing the frames per second of the video to 2
    cap.set(cv2.CAP_PROP_FPS, 2)   
    # Used as counter variable 
    x=1
    frameRate = cap.get(5) #frame rate
    numberOfPicturesPerSecond= 2
    blockBlobService = BlockBlobService(account_name='stworkersafety', account_key='7OyzTj7Y83+0/+DiuS9IVDoZcKrQ0pSjE4F4q8L/ltT+Dv4TbBXTSDrOu928L60SCzo7mq+P3fEv3B4aOL6Flw==')
    # start creating frames from video
    while(cap.isOpened()):
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
            pilImage = pilImage.resize(size, Image.ANTIALIAS)
            imgByteArr = BytesIO()
            pilImage.save(imgByteArr, format='jpeg')
            #print(type(pilImage))          
            imgByteArr = imgByteArr.getvalue()
            
            # write image to blob for logging
            now = datetime.strftime(datetime.now(), "%Y%m%dT%H%M%S%Z")
            imageFileName= 'epm_stage/image' +  str(int(x)) + "_img_" + now + ".jpg"
            #imageFileName= 'folder' + "/log/image" +  str(int(x)) + "_img.png"
            blockBlobService.create_blob_from_bytes('videoblob', imageFileName, imgByteArr)
            #Write to local directory
            pilImage.save(os.path.join(pathOut , "image{:d}.jpg".format(x)))
            #cv2.imwrite(os.path.join(pathOut , "image{:d}.jpeg".format(x)),frame)
         # increment image
            x+=1
            
def uploadtoblob(filepath):
    block_blob_service = BlockBlobService(account_name='stworkersafety', account_key='7OyzTj7Y83+0/+DiuS9IVDoZcKrQ0pSjE4F4q8L/ltT+Dv4TbBXTSDrOu928L60SCzo7mq+P3fEv3B4aOL6Flw==')
    container_name ='videoblob\\epm_stage'

    #local_path = "D:\\Test\\test"

    for files in os.listdir(filepath):
        block_blob_service.create_blob_from_path(container_name,files,os.path.join(filepath,files),timeout=1000)          


def main():
    print('Reached here')
   # extractFrames('D:\\Demo & Utilities\\Worker Safety\\Unattended Hazardeous Object\\Frames Generated'
   #               )
   #folder_path = '.\\FramesGenerated\\'
   #for file_name in listdir(folder_path):
   #        if file_name.endswith('.jpg'):  
   #            os.remove(folder_path + file_name)

    media_path = '.\\media\\'
    for file_name in listdir(media_path)
            print(os.path.join('./media', filename))
            #extractFrames('./FramesGenerated' , os.path.join('./media', filename) )
   #uploadtoblob('./FramesGenerated')

if __name__ == '__main__':
    main()

