import cv2
import numpy
import  numpy as np

path = "Resources/shape.png"
img = cv2.imread(path)



def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray [0])
    rowsAvailable = isinstance(imgArray [0], list)
    width = imgArray [0][0].shape[1]
    height = imgArray [0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray [x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray [x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray [x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor =[imageBlank]*rows
        hor_con =[imageBlank]*rows
        for x in range(0, rows):
            hor [x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):

            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)

            else:
             imgArray  [x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray [x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver

def getEdges(img):
    edges,hierarchy=cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for edge in edges:
        area = cv2.contourArea(edge)
        print(area)
        if area > 500 :
            cv2.drawContours(imgCont, edge, -1, (255, 0, 0), 3)
            par = cv2.arcLength(edge,True)
            print(par)
            approx = cv2.approxPolyDP(edge,0.02*par,True)
            print(len(approx))
            objCorner = len(approx)
            x, y, w, h = cv2.boundingRect(approx)
            if objCorner==3:
                objType="Triangle"
            elif objCorner == 4:
                asRatio = w / float(h)
                if asRatio > 0.95 and asRatio< 1.05:
                    objType = "Square"
                else:
                    objType= "Rectangle"
            else:
                objType="Circle"
            cv2.rectangle(imgCont,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(imgCont,objType,(x+(w//2)-10,y+(h//2)),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255,2))




imgCont=img.copy()

imgGray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
imgBlur=cv2.GaussianBlur(imgGray,(7,7),1)
imgCanny = cv2.Canny(imgBlur,50,50)
getEdges(imgCanny)


black = numpy.zeros_like(img)

stack = stackImages(0.5,([img,imgGray,imgBlur],[imgCanny,imgCont,black]))
cv2.imshow("stack",stack)
cv2.waitKey(0)

