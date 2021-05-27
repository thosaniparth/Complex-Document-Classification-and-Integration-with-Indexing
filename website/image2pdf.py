import img2pdf 
from django import views
from django.conf import settings
from PIL import Image 
import os 
  
# storing image path

def create_pdf(img_list): 
    img_path = img_list
    print('inside create pdf',img_list)
    pdf_path = 'first.pdf'
    image = Image.open(img_path) 
    pdf_bytes = img2pdf.convert(image.filename) 
    file = open(pdf_path, "wb") 
    image.close() 
    file.write(pdf_bytes) 
     
  
# closing pdf file 
    file.close() 
  
def create_pdf1(img_list): 
    img_path = img_list
    print('inside create pdf',img_list)
    pdf_path = 'second.pdf'
    image = Image.open(img_path) 
    pdf_bytes = img2pdf.convert(image.filename) 
    file = open(pdf_path, "wb") 
    image.close() 
    file.write(pdf_bytes) 
    file.close()
# img_path1 = views.img_list1
# # storing pdf path 
# pdf_path1= os.path.join(settings.BASE_DIR,"PDF")
# # opening image 
# image1=Image.open(img_path1)
# # converting into chunks using img2pdf 
# pdf_bytes1 =img2pdf.convert(image1.filename)
# # opening or creating pdf file 
  
# # writing pdf files with chunks 

# file1 = open(pdf_path1,"wb")
# file1.write(pdf_bytes1)
  
# closing image file 

# output 
print("Successfully made pdf file") 