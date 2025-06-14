import numpy as np
import cv2
import os
import random
import pickle
from imutils import paths
from scipy.spatial import distance

#PATH or folder name of dataset
PATH = 'dataset'
# Train and test factor. 80% is used for training. 20% for testing.
TRAIN_FACTOR = 80
# please reduce TOTAL_IMAGES value to 800 or less if you are facing memory issues.
TOTAL_IMAGES = 100
N_CLASSES = 35
# clustering factor
CLUSTER_FACTOR = 8

# START and END are rectangle coordinates (ROI) which is displayed on camera frame. Please use them accordingly based on your system.
# mac
#START = (450,75)
#END = (800,425)
##
# windows
START = (300,75)
END = (600,400) 
##
IMG_SIZE = 128



def get_canny_edge(image):
   
    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Convert from RGB to HSV
    HSVImaage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 

    # Finding pixels with itensity of skin
    lowerBoundary = np.array([0,40,30],dtype="uint8")
    upperBoundary = np.array([43,255,254],dtype="uint8")
    skinMask = cv2.inRange(HSVImaage, lowerBoundary, upperBoundary)
    
    # blurring of gray scale using medianBlur
    skinMask = cv2.addWeighted(skinMask,0.5,skinMask,0.5,0.0)
    skinMask = cv2.medianBlur(skinMask, 5)
    skin = cv2.bitwise_and(grayImage, grayImage, mask = skinMask)
    #cv2.imshow("masked2",skin)
    
    #. canny edge detection
    canny = cv2.Canny(skin,60,60)
    #plt.imshow(img2, cmap = 'gray')
    return canny,skin

def get_SIFT_descriptors(canny):
    # Initialising SIFT
    sift = cv2.SIFT_create()
    canny = cv2.resize(canny, (256, 256))
    # computing SIFT descriptors
    kp, des = sift.detectAndCompute(canny, None)
    return des

# Find the index of the closest central point to the each sift descriptor.   
def find_index(image, center):
    count = 0
    index = 0
    for i in range(len(center)):
        if(i == 0):
           count = distance.euclidean(image, center[i]) 
        else:
            calculated_distance = distance.euclidean(image, center[i]) 
            if(calculated_distance < count):
                index = i
                count = calculated_distance
    return index

def get_labels():
    class_labels = []
    for (dirpath,dirnames,filenames) in os.walk(PATH):
        dirnames.sort()
        for label in dirnames:
            #print(label)
            if not (label == '.DS_Store'):
                class_labels.append(label)
    
    return class_labels

def get_all_gestures():
    gestures = []
    for (dirpath,dirnames,filenames) in os.walk(PATH):
        dirnames.sort()
        for label in dirnames:
            #print(label)
            if not (label == '.DS_Store'):
                for (subdirpath,subdirnames,images) in os.walk(PATH+'/'+label+'/'):
                    random.shuffle(images)
                    #print(label)
                    imagePath = PATH+'/'+label+'/'+images[0]
                    #print(imagePath)
                    img = cv2.imread(imagePath)
                    img = cv2.resize(img, (int(IMG_SIZE * 3/4),int(IMG_SIZE* 3/4)))
                    img = cv2.putText(img, label, (5,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255), 1, cv2.LINE_AA)
                    gestures.append(img)
    
    print('length of gesatures {}'.format(len(gestures)))
    im_tile = concat_tile(gestures, (5, 7))
   # im_tile = concat_tile(gestures, (2, 2))
    

    return im_tile

def concat_tile(im_list_2d, size):
    count = 0
    all_imgs = []
    for row in range(size[1]):
        imgs = []
        for col in range(size[0]):
            imgs.append(im_list_2d[count])
            count += 1
        all_imgs.append(imgs)    
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in all_imgs])

