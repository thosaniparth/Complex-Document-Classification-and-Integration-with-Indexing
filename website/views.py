from django.shortcuts import render
from django.views.generic import TemplateView,CreateView
from django.urls import reverse_lazy
# from .models import Person
# from .forms import POSTform
from django.http import HttpResponseRedirect
from django.http import FileResponse

# import pymongo
import cv2
from django.conf import settings

# from bootstrap_modal_forms.generic import BSModalReadView

# Create your views here.
import numpy as np
import cv2
from .contour import *
from .ocrtest import *
from .apps import WebsiteConfig
from .forms import POSTform
from .models import PostModel
from .merge import *
from .image2pdf import *
from django.http import HttpResponse

import os

# import pymongo
# import base64

# # Mongo DB temperory details storage

# client=pymongo.MongoClient("mongodb+srv://prod_user:DocClass123@cluster0.ndl4b.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
# db = client['myFirstDatabase']
# collection = db['collection']
# b=0
# f=0
# filepath = r'C:\Users\Admin\Downloads\Django_Form\MergedFiles.pdf'
# with open(filepath, "rb") as image:
#   f = image.read()
#   b = bytearray(f)
# pan_card=base64.b64encode(b)
# person={"name":"TEST123",
#         "email":"test@test.com",
#         "dob":"11/11/1999",
#         "Pan Number":"EDOPS0070M",
#         "Pan card":pan_card
#     }

# person_id=db.collection.insert_one(person).inserted_id
# print(person_id)

class Home(TemplateView):
    template_name = 'home.html'


# class PersonInfo(BSModalReadView):
#     model = Person
#     template_name = 'modal_result.html'

class Upload(CreateView):
    model = PostModel
    form_class = POSTform
    template_name = 'upload.html'
    success_message = 'Success: Details were received.'
    success_url = reverse_lazy('home')

def upload(request):
    return render(request, 'upload.html', {'form': form})

def results(request):
    return render(request, 'result.html', {})

def merged_docs(request):
    filepath = r'C:\Users\Admin\Downloads\Django_Form\MergedFiles.pdf'
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')

def about(request):
    return render(request, 'about.html', {})


def get_img_from_bytes(image_bytes):
    decoded = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
    return decoded

def model_prediction(image):
    documents=["Aadhar","Driving_license","PAN"]

    width=200
    height=200

    resized_img=cv2.resize(image,(height,width),interpolation=cv2.INTER_AREA)
    # print(resized_img.shape)
    resized_img = resized_img[None,...]
    prediction = WebsiteConfig.model.predict(resized_img)
    print(prediction)
    if np.any(prediction >= 0.8):
        print("test")
        return documents[np.argmax(prediction)]
    else:
        return "Invalid Document!!!"



def save(request):

    if request.method == 'POST':
                
        form=POSTform(request.POST,request.FILES)
        if form.is_valid():
            name= form.cleaned_data.get("name")
            middlename= form.cleaned_data.get("middlename")
            surname = form.cleaned_data.get("surname")
            dob= form.cleaned_data.get("dob")
            image =form.cleaned_data.get("image")
            image1=form.cleaned_data.get("image1")
            initial_obj = form.save()
        
        # dictforPAN = ocr_main.dictValuesforPAN
        # dictforAadhar = ocr_main.dictValuesforAadhar
        # context= {'form': form, 'name':name, 'middlename':middlename,'surname':surname,'dob':dob}
        

        # print("Path",request.FILES)
        # image1=get_img_from_bytes(image.read())
        # old = initial_obj.image.url
        # img_list =os.listdir(settings.MEDIA_ROOT+'\pictures\pan.jpg')
        # img_list = r'C:\Users\Admin\Desktop\MP2\pan.jpg'
        # basic_dir = r'C:\\Users\\Admin\\Downloads'
        print("settings media root",settings.MEDIA_ROOT)
        print("initia_obj_image_url",initial_obj.image.url[1:])
        newPath = initial_obj.image.url[1:].replace('/','\\')
        img_list = os.path.join(settings.BASE_DIR,newPath)

        print('Image_list',img_list)
        image = cv2.imread(img_list)
        document=model_prediction(image)
        print(document)
        
        form_name = name
        form_middlename = middlename
        form_surname = surname

        if document!="Invalid Document!!!":
            blurred_threshold = transformation(image)
            cleaned_image = final_image(blurred_threshold,image)

            dictValuesforAadharforFirst, dictValuesforPANforFirst = ocr_main(cleaned_image,document,form_name,form_middlename,form_surname)

           
            create_pdf(img_list)
        else:
            print("ERROR!")


        print("settings media root",settings.MEDIA_ROOT)
        # print("initia_obj_image_url",initial_obj.image1.url[1:])
        newPath1 = initial_obj.image1.url[1:].replace('/','\\')
        img_list1 = os.path.join(settings.BASE_DIR,newPath1)

        print('Image_list',img_list1)
        image1 = cv2.imread(img_list1)
        document1=model_prediction(image1)
        print(document1)
        

        if document1!="Invalid Document!!!":
            blurred_threshold = transformation(image1)
            cleaned_image = final_image(blurred_threshold,image1)

            dictValuesforAadharforSecond, dictValuesforPANforSecond= ocr_main(cleaned_image,document1,form_name,form_middlename,form_surname)
            create_pdf1(img_list1)

        else:
            print("ERROR!")

        merge_pdf()
        
        context= {'form': form, 'name':name, 'middlename':middlename,'surname':surname,'dob':dob,'dictValuesforAadharforFirst':dictValuesforAadharforFirst,'dictValuesforPANforFirst':dictValuesforPANforFirst,'dictValuesforAadharforSecond':dictValuesforAadharforSecond,'dictValuesforPANforSecond':dictValuesforPANforSecond}
        
        # filepath = r'C:\Users\Admin\Downloads\Django_Form\MergedFiles.pdf'
        # return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
        return render(request, 'result.html', context)
    else:
        form = POSTform()
        return render(request, 'upload.html', {'form': form})
            
        

