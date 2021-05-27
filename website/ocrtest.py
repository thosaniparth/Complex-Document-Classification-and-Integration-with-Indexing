from PIL import Image
import pytesseract
import numpy as np
from pytesseract import Output
import cv2
import matplotlib.pyplot as plt
import re
import random
# import image_slicer
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#https://www.thepythoncode.com/article/optical-character-recognition-pytesseract-python


def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)
 
#thresholding
def get_thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#dilation
def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)
    
#erosion
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def get_opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

def get_canny(image):
    return cv2.Canny(image, 100, 200)

def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
    
def ocr_main(image,document,form_name,form_middlename,form_surname):
    date_of_birth = '^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)\d\d$'
    gender = '(Fem|M)ale'
    gender1 = '(FEM|M)ALE'
    aadhar_pattern = '^([0-9][0-9][0-9][0-9])'
    percent="^([0-9][0-9].[0-9][0-9])"
    pan_pattern = '^([A-Z][A-Z][A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9][A-Z])'
    name = form_name
    middlename = form_middlename
    surname = form_surname
    # image_slicer.slice('ssc.jpeg', 4)

    # image_original = cv2.imread('ssc2.jpeg')
    # y1 = random.randint(0,2200)
    # y2 = random.randint(2200,10000)
    # print(y1)
    # print(y2)
    # image = image_original[530:1010,20:330]
    # image = cv2.imread('slice_disha_1.png')
    # image_type = 'PAN'
    image_type = document

    # FOR SSC MARKSHEET ONLY 
    # image= image_resize(image, height = 600)

    dictValuesforPAN = {
    "Name": "",
    "Middlename":"",
    "Surname":"",
    "Dateofbirth": "",
    "PAN":"",
    }
    dictValuesforAadhar  = {
    "Name": "",
    "Middlename":"",
    "Surname":"",
    "Dateofbirth": "",
    "Gender": "",
    "AadharNumber": [],
    }
    dictValuesforDL  = {
    "Name": "",
    "Middlename":"",
    "Surname":"",
    "Dateofbirth": "",
    "Gender": "",
    "DrivingLicence" : ""
    }

    gray = get_grayscale(image)

    thresholding= get_thresholding(gray)
    opening = get_opening(gray)
    canny = get_canny(gray)
    if image_type==document:
        
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV) 
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18)) 

        # Appplying dilation on the threshold image 
        dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1) 

        # Finding contours 
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

        image = image.copy() 
        rgb_planes = cv2.split(image)

        result_planes = []
        result_norm_planes = []

        for plane in rgb_planes:
            
            dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 15)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(diff_img*2)
            result_norm_planes.append(norm_img)
            

        image = cv2.merge(result_planes)
        image = cv2.merge(result_norm_planes)

        # plt.imshow(image)
        # plt.show()
        new_text = []
        for cnt in contours: 
            x, y, w, h = cv2.boundingRect(cnt)
            
            cropped = image[y:y + h, x:x + w]
            text = pytesseract.image_to_string(cropped)
            new_text.extend(text.split())
            # plt.imshow(cropped)
            # plt.show()   
        


        for i in range(0, len(new_text)):
            if re.match(aadhar_pattern.lower() , new_text[i].lower()) and image_type=="Aadhar":
                    dictValuesforAadhar["AadharNumber"].append(new_text[i])
        
            if re.match(gender1.lower(),new_text[i].lower()) and image_type=="Aadhar":
                        if dictValuesforAadhar["Gender"] == "":
                            dictValuesforAadhar["Gender"] = (new_text[i])

            if re.match(gender1.lower(),new_text[i].lower()) and image_type=="DL":
                        if dictValuesforDL["Gender"] == "":
                            dictValuesforDL["Gender"] = (new_text[i])

            if re.match(gender.lower(),new_text[i].lower()) and image_type=="Aadhar":
                        if dictValuesforAadhar["Gender"] == "":
                            dictValuesforAadhar["Gender"] = (new_text[i])

            if re.match(gender.lower(),new_text[i].lower()) and image_type=="DL":
                        if dictValuesforDL["Gender"] == "":
                            dictValuesforDL["Gender"] = (new_text[i])

            if re.match(pan_pattern.lower(),new_text[i].lower()) and image_type=="PAN":
                        if dictValuesforPAN["PAN"] == "":
                            dictValuesforPAN["PAN"] = (new_text[i])
                    
            if re.match(date_of_birth.lower(),new_text[i].lower()) and image_type=="Aadhar":
                        if dictValuesforAadhar["Dateofbirth"] == "":
                            dictValuesforAadhar["Dateofbirth"] = (new_text[i])

            if re.match(date_of_birth.lower(),new_text[i].lower()) and image_type=="PAN":
                        if dictValuesforPAN["Dateofbirth"] == "":
                            dictValuesforPAN["Dateofbirth"] = (new_text[i])

            if re.match(date_of_birth.lower(),new_text[i].lower()) and image_type=="DL":
                        if dictValuesforDL["Dateofbirth"] == "":
                            dictValuesforDL["Dateofbirth"] = (new_text[i])

            if re.match(name.lower(),new_text[i].lower()) and image_type=="Aadhar":
                        if dictValuesforAadhar["Name"] == "":
                            dictValuesforAadhar["Name"] = (new_text[i])
            
            if re.match(name.lower(),new_text[i].lower()) and image_type=="PAN":
                        if dictValuesforPAN["Name"] == "":
                            dictValuesforPAN["Name"] = (new_text[i])

            if re.match(name.lower(),new_text[i].lower()) and image_type=="DL":
                        if dictValuesforDL["Name"] == "":
                            dictValuesforDL["Name"] = (new_text[i])

            if re.match(middlename.lower(),new_text[i].lower()) and image_type=="Aadhar":
                        if dictValuesforAadhar["Middlename"] == "":
                            dictValuesforAadhar["Middlename"] = (new_text[i])

            if re.match(middlename.lower(),new_text[i].lower()) and image_type=="PAN":
                        if dictValuesforPAN["Middlename"] == "":
                            dictValuesforPAN["Middlename"] = (new_text[i])

            if re.match(surname.lower(),new_text[i].lower()) and image_type=="Aadhar":
                        if dictValuesforAadhar["Surname"] == "":
                            dictValuesforAadhar["Surname"] = (new_text[i])

            if re.match(surname.lower(),new_text[i].lower()) and image_type=="PAN":
                        if dictValuesforPAN["Surname"] == "":
                            dictValuesforPAN["Surname"] = (new_text[i])        

            if re.match(surname.lower(),new_text[i].lower()) and image_type=="DL":
                        if dictValuesforDL["Surname"] == "":
                            dictValuesforDL["Surname"] = (new_text[i])
            print("NEW TEXT",new_text)
                    
    else:
        print("Not PAN")        


    results = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    # print(results.keys())
    # print(results['text'])

    for i in range(0, len(results["text"])):
        
        
        text = results["text"][i]
    
        w = results["width"][i]
        h = results["height"][i]
        l = results["left"][i]
        t = results["top"][i]
        # define all the surrounding box points
        p1 = (l, t)
        p2 = (l + w, t)
        p3 = (l + w, t + h)
        p4 = (l, t + h)
        # draw the 4 lines (rectangular)
    
        text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
    if re.match(aadhar_pattern.lower() , results['text'][i].lower()) and image_type=="Aadhar":
                dictValuesforAadhar["AadharNumber"].append(results['text'][i])
    
    if re.match(gender1.lower(),results["text"][i].lower()) and image_type=="Aadhar":
                if dictValuesforAadhar["Gender"] == "":
                    dictValuesforAadhar["Gender"] = (results["text"][i])

    if re.match(gender1.lower(),results["text"][i].lower()) and image_type=="DL":
                if dictValuesforDL["Gender"] == "":
                    dictValuesforDL["Gender"] = (results["text"][i])

    if re.match(gender.lower(),results["text"][i].lower()) and image_type=="Aadhar":
                if dictValuesforAadhar["Gender"] == "":
                    dictValuesforAadhar["Gender"] = (results["text"][i])

    if re.match(gender.lower(),results["text"][i].lower()) and image_type=="DL":
                if dictValuesforDL["Gender"] == "":
                    dictValuesforDL["Gender"] = (results["text"][i])

    if re.match(pan_pattern.lower(),results["text"][i].lower()) and image_type=="PAN":
                if dictValuesforPAN["PAN"] == "":
                    dictValuesforPAN["PAN"] = (results["text"][i])
            
    if re.match(date_of_birth.lower(),results["text"][i].lower()) and image_type=="Aadhar":
                if dictValuesforAadhar["Dateofbirth"] == "":
                    dictValuesforAadhar["Dateofbirth"] = (results["text"][i])

    if re.match(date_of_birth.lower(),results["text"][i].lower()) and image_type=="PAN":
                if dictValuesforPAN["Dateofbirth"] == "":
                    dictValuesforPAN["Dateofbirth"] = (results["text"][i])


    if re.match(date_of_birth.lower(),results["text"][i].lower()) and image_type=="DL":
                if dictValuesforDL["Dateofbirth"] == "":
                    dictValuesforDL["Dateofbirth"] = (results["text"][i])

    if re.match(name.lower(),results["text"][i].lower()) and image_type=="Aadhar" :
                if dictValuesforAadhar["Name"] == "":
                    dictValuesforAadhar["Name"] = (results["text"][i])
    
    if re.match(name.lower(),results["text"][i].lower()) and image_type=="PAN":
                if dictValuesforPAN["Name"] == "":
                    dictValuesforPAN["Name"] = (results["text"][i])

    if re.match(name.lower(),results["text"][i].lower()) and image_type=="DL":
                if dictValuesforDL["Name"] == "":
                    dictValuesforDL["Name"] = (results["text"][i])

    if re.match(middlename.lower(),results["text"][i].lower()) and image_type=="Aadhar":
                if dictValuesforAadhar["Middlename"] == "":
                    dictValuesforAadhar["Middlename"] = (results["text"][i])

    if re.match(middlename.lower(),results["text"][i].lower()) and image_type=="PAN":
                if dictValuesforPAN["Middlename"] == "":
                    dictValuesforPAN["Middlename"] = (results["text"][i])

    if re.match(surname.lower(),results["text"][i].lower()) and image_type=="Aadhar":
                if dictValuesforAadhar["Surname"] == "":
                    dictValuesforAadhar["Surname"] = (results["text"][i])

    if re.match(surname.lower(),results["text"][i].lower()) and image_type=="PAN":
                if dictValuesforPAN["Surname"] == "":
                    dictValuesforPAN["Surname"] = (results["text"][i])        

    if re.match(surname.lower(),results["text"][i].lower()) and image_type=="DL":
                if dictValuesforDL["Surname"] == "":
                    dictValuesforDL["Surname"] = (results["text"][i])
 
        # if re.match(percent,results['text'][i]): 
                    # print('Percent',results['text'][i])
                    
        # cv2.imshow("Image", image)


    # show the output image
    print(dictValuesforAadhar)
    print(dictValuesforDL)
    print(dictValuesforPAN)
    # cv2.imshow("Image", image)
    # cv2.waitKey(0)

    return dictValuesforAadhar,dictValuesforPAN

