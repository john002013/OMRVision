import cv2
import numpy as np

import Utils
#import numpy as np
################################
width_resize = 700
height_resize = 700
answers = [1,2,0,1,3]
Choices =5
Questions =5
webcamFeed = True
################################
#img = cv2.imread('1.jpg')
cap = cv2.VideoCapture(1)
cap.set(10,150)

while True:
    if webcamFeed: sucess, img = cap.read()
    else: img = cv2.imread('1.jpg')

    #Preprocessing
    img = cv2.resize(img,(width_resize,height_resize))
    imgContours = img.copy()
    Img_Final = img.copy()
    Grading_Final = img.copy()
    imgbiggsetcontour = img.copy()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
    #To detect edges we use canny function#
    Edge_detector = cv2.Canny(imgBlur,10,50)
    ############################################################
    try:
        #Countor detection#
        contours, hierarchy = cv2.findContours(Edge_detector, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(imgContours,contours,-1,(0,255,100),2)
        #################################################################

        #Finding Rectangle in contours
        rectCon = Utils.rectContours(contours)
        biggestContour = Utils.cornerpoints(rectCon[0])
        gradePoints = Utils.cornerpoints(rectCon[1])

        if biggestContour.size != 0 and gradePoints.size !=0:
            cv2.drawContours(imgbiggsetcontour,biggestContour, -1,(0,255,100), 15 )
            cv2.drawContours(imgbiggsetcontour,gradePoints, -1, (0, 255, 100), 15)

            biggestContour= Utils.reorder(biggestContour)
            gradePoints = Utils.reorder(gradePoints)

            point1 = np.float32(biggestContour)
            point2 = np.float32([[0,0],[width_resize,0],[0,height_resize],[width_resize,height_resize]])
            matrix = cv2.getPerspectiveTransform(point1,point2)
            warp = cv2.warpPerspective(img,matrix,(width_resize,height_resize))

            pointg1 = np.float32(gradePoints)
            pointg2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])
            matrixg = cv2.getPerspectiveTransform(pointg1, pointg2)
            warpg = cv2.warpPerspective(img, matrixg, (325, 150))
            #cv2.imshow("grade", warpg)

            #Applying Threshold########
            warpGray = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)
            warpThrehold = cv2.threshold(warpGray,170,255,cv2.THRESH_BINARY_INV)[1]

            #split############
            boxes = Utils.split(warpThrehold)
            #cv2.imshow('Test', boxes[2])


            ###To get Non-Zero Pixel values of each box###
            #print(cv2.countNonZero(boxes[1]),cv2.countNonZero(boxes[2]))

            pixels = np.zeros((Questions,Choices))
            countCols = 0
            countRows = 0

            for image in boxes:
                totalPixels = cv2.countNonZero(image)
                pixels[countRows][countCols] = totalPixels
                countCols +=1
                if (countCols ==Choices):countRows +=1 ; countCols =0
            #print

        #******Finding Maximum Pixels******#
            Index = []
            for x in range(0,Questions):
                array = pixels[x]
                indexVal = np.where(array==np.amax(array))
                #print(indexVal[0])
                Index.append(indexVal[0][0])

        #******Comparing answers for grading******#
            Gradings = []
            for x in range (0,Questions):
                if answers[x] == Index[x]:
                    Gradings.append(1)
                else: Gradings.append(0)
            #print(Gradings)
            score = sum(Gradings)/5 * 100 #Final Grade
            print(score)

        ##DISPLAYING ANSWERS##
            Result = warp.copy()
            Result = Utils.Show(Result,Index,Gradings,answers,Questions,Choices)
        ###Extracting Coloured Mark Circle################################################
            Extract = np.zeros_like(warp)
            Extract = Utils.Show(Extract, Index, Gradings, answers, Questions, Choices)
        ######################################################################################

            matrix_Final = cv2.getPerspectiveTransform(point2, point1)
            warp_final = cv2.warpPerspective(Extract, matrix_Final, (width_resize, height_resize))
        #Extraction for Grading box########
            Extract_Grading = np.zeros_like(warpg)
            cv2.putText(Extract_Grading,str(int(score/10))+"/10",(60,100),cv2.FONT_HERSHEY_COMPLEX,2,(0,255,255),3)

            matrixg_Final = cv2.getPerspectiveTransform(pointg2, pointg1)
            warpg_Final = cv2.warpPerspective(Extract_Grading, matrixg_Final, (width_resize, height_resize))


            Img_Final = cv2.addWeighted(Img_Final,1,warp_final,1, 0)
            Img_Final = cv2.addWeighted(Img_Final, 1, warpg_Final, 1, 0)

        #stacking#
        imgBlank = np.zeros_like(img)
        ImgArray = ([img, imgGray, imgBlur, Edge_detector],
                    [imgContours, imgbiggsetcontour, warp, warpThrehold],
                    [Result, Extract, warp_final, Img_Final])

    except:
        imgBlank = np.zeros_like(img)
        ImgArray =  ([img,imgGray,imgBlur,Edge_detector],
                    [imgBlank,imgBlank,imgBlank,imgBlank],
                    [imgBlank,imgBlank,imgBlank,imgBlank])
    Labels = [["Original","Gray","Blur","Canny"],
              ["Contour","Biggest_Contour","Warp","Threshold"],
              ["Result","Raw_Drawing","In_Warp","Final"]]
    Stack_img = Utils.stackImages(ImgArray,0.3, Labels)
    ############################################################
    cv2.imshow("Final",Img_Final)
    cv2.imshow('Ace', Stack_img)
    if cv2.waitKey(1) & 0xFF ==ord('s'):
        cv2.imwrite("Final.jpg",Img_Final)
        cv2.waitKey(300)
        cv2.destroyAllWindows()
