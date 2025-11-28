import cv2
import numpy as np

def stackImages(imgArray,scale,lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        hor_con= np.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth= int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        #print(eachImgHeight)
        for d in range(0, rows):
            for c in range (0,cols):
                cv2.rectangle(ver,(c*eachImgWidth,eachImgHeight*d),(c*eachImgWidth+len(lables[d][c])*13+27,30+eachImgHeight*d),(255,255,255),cv2.FILLED)
                cv2.putText(ver,lables[d][c],(eachImgWidth*c+10,eachImgHeight*d+20),cv2.FONT_HERSHEY_COMPLEX,0.3,(255,0,255),1)
    return ver

def rectContours(contours):
    rectCon= []
    for i in contours:
        area= cv2.contourArea(i)
       # print("Area:", area)
        if area>50:
            perimeter = cv2.arcLength(i, True)
            approximate =cv2.approxPolyDP(i, 0.02*perimeter, True)
            #print("Contours:", len(approximate))
            if len(approximate) == 4:
                rectCon.append(i)
    rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)
    return rectCon
def cornerpoints(cont):
    perimeter = cv2.arcLength(cont, True)
    approximate = cv2.approxPolyDP(cont, 0.02 * perimeter, True)
    return approximate

def reorder(points):
  points = points.reshape((4,2))
  pointsNew = np.zeros((4,1,2), np.int32)
  add = points.sum(1)
  #print(points)
  #print(add)
  pointsNew[0] = points[np.argmin(add)] #(0,0)
  pointsNew[3] = points[np.argmax(add)] #(w,h)
  diff = np.diff(points,axis=1)
  pointsNew[1]= points[np.argmin(diff)] #(w, 0)
  pointsNew[2] = points[np.argmax(diff)] #(h, 0)
  #print(diff)

  return pointsNew

def split(img):
    rows = np.vsplit(img,5)
    boxes = []
    for r in rows:
        cols = np.hsplit(r,5)
        for box in cols:
            boxes.append(box)
            #cv2.imshow('split',box)

    return boxes

def Show(img,Index,Gradings,answers,Questions,Choices):
    secW = int(img.shape[1]/Questions)
    secH = int(img.shape[0]/Choices)

    for x in range (0,Questions):
        Myans = Index[x]
        cx = (Myans*secW)+secW//2
        cy = (x*secH)+secH//2

        if Gradings[x] ==1:
            myColor = (0,255,0)
        else: myColor = (0,0,255)

        cv2.circle(img,(cx,cy),30,myColor,cv2.FILLED)

    return img












