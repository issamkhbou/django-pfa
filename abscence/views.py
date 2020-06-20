from .models import * 
from .serializers import * 
from rest_framework import  viewsets ,status
from rest_framework.response import  Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.conf import settings

from rest_framework.filters import  SearchFilter ,  OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .decoding import decode_base64_file 
from .facerec_from_webcam import detect_faces_in_image 
from .generate_xlsx import generateXlsx 
from .getAbsenceInSingleCourse import countAbs , getRow 
from .send_email_to_teacher import send_mail_with_excel 

import json 
import os 
import uuid
from base64 import b64encode
import face_recognition
import base64
import six
import imghdr

from django.core.files.base import ContentFile
import datetime



# Create your views here.
class StudentViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter ]
    serializer_class = StudentSerializer
    filter_fields =('classe',)
    search_fields =('name',) # not working 
    ordering_fields =('id',"name") #or we can use '__all__'
    #ordering =('id',) # default order 
    queryset = Student.objects.all()
    #lookup_field= "name" #/customer/"issam" instead of using /customer/1

    """ def get_queryset(self):
        #import pdb; pdb.set_trace() 'break point !'
        id = self.request.query_params.get('id',None)
        if self.request.query_params.get('active')=='False' :
            status = False 
        else : 
            status = True
        
        if id : 
            students = Student.objects.filter(id=id , active=status)
        else : 
            students = Student.objects.filter(active=status)

        return students """

    
    def get_querysetByClass(self):
        #import pdb; pdb.set_trace() 'break point !'
        classe = self.request.query_params.get('classe',None)
        
        if classe : 
            #students = Student.objects.filter(address__icontains= address )
            students = Student.objects.filter(classe=classe)

        else : 
            students = Student.objects.all()
        return students
    #TOTRY : na3mel methode mte3i mta3 recogn fi hal classe w 
    #mba3d namel list 3ali saret 3lihom reconnaissance

    def list(self, request,*args,**kwargs):                 #working
        students = self.get_querysetByClass()
        #students = Student.objects.filter(id=1)
        serializer = StudentSerializer(students,many=True)
        return Response(serializer.data)

    def retrieve(self,request,*args,**kwargs):             #working
        student = self.get_object()
        serializer = StudentSerializer(student) 
        return Response(serializer.data)

    def create(self,request,*args,**kwargs):               #working
        data = request.data 
        
        #image = data['image']
        #newFileName = data['name'] + ".jpg"
        #path = os.path.join(settings.MEDIA_URL ,"students",newFileName)
        #starter = image.find(',')
        #image = image[starter+1:]
        #decoded_file = base64.b64decode(image)
        #image = ContentFile(decoded_file, name=newFileName)
        #default_storage.save(path,image)


        image = decode_base64_file(data["image"], data['name'])
        student = Student.objects.create(
            name = data['name'] ,
            cin = data['cin'] ,
            classe = data['classe'],
            email = data['email'],
            password = data['password'],
            image=image
            #imagePath = path
             )

        student.save()

        serializer = StudentSerializer(student)
        return Response(serializer.data) 



    def update(self,request,*args,**kwargs): #working
        student = self.get_object()
        data = request.data 
        student.name = data['name']
        student.cin = data['cin']
        student.classe = data['classe']
        student.email = data['email']
        student.password = data['password']

        student.save()

        serializer = StudentSerializer(student)
        return Response(serializer.data)

    
    #PATCH request
    def partial_update(self,request,*args,**kwargs): #working
        student = self.get_object()
        student.name = request.data.get('name',student.name)
        student.cin = request.data.get('cin',student.cin)
        student.email = request.data.get('email',student.email)
        student.password = request.data.get('password',student.password)
        student.classe = request.data.get('classe',student.classe)

        student.save()

        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def destroy(self,request,*args,**kwargs): #working
        student = self.get_object()
        student.delete()

        imgage = os.path.join("media","students",student.name+".jpg") 
        os.remove(imgage)

        return Response("successefully removed")


@api_view(['GET',"POST"])
def upload(request):
    data = request.data 
    image = data['image']
    course = data['course']
    classe=data['classe']
    id = data['id']  
    recipient_email = data['recipient_email'] 

    newFileName = 'test'+str(id)+".jpg"
    path = os.path.join(settings.MEDIA_URL ,"uploads",newFileName)

    starter = image.find(',')
    image = image[starter+1:]
    decoded_file = base64.b64decode(image)
    image = ContentFile(decoded_file, name=newFileName)
    default_storage.save(path,image)

    frame = face_recognition.load_image_file(os.path.join("media",path))
    studentsNames = detect_faces_in_image(frame)
    print(studentsNames)####
    presents=[]
    for studentName in studentsNames :
        presents.append(Student.objects.filter(name=studentName)[0])
    all = list(Student.objects.filter(classe=classe))
    d = datetime.datetime.today()

    excelFileName =os.path.join("media",'courses',course,classe,"Liste "+classe+" "+d.strftime('%d-%m-%Y')+".xlsx")   
    generateXlsx(excelFileName,all,presents)

    recipient_email="pfaenis1@gmail.com"
    send_mail_with_excel(recipient_email,classe,excelFileName)
    print(presents) ####
    serializer = StudentSerializer(presents,many=True)
    return Response(serializer.data)

@api_view(['GET',"POST"])
def getAbsence(request):
    data = request.data 
    course = data['course']
    classe=data['classe']
    name = data['name']

    path =  os.path.join("media","courses",course, classe)
     
    all = list(Student.objects.filter(classe=classe))

    files = os.listdir(path) 
    #getting the student pos in stylesheet(feuille d'appel)
    positionInSheet = getRow(name, os.path.join(path,files[0]) )
    count ,dates = countAbs(name,path,positionInSheet)
    output = {
        "abscenceTimes" : count ,
        "dates" : dates
    }
    return Response({"Nombre d'abscence":output})



def upload_image(request):
    img = request.FILES['image']
    img_extension = os.path.splitext(img.name)[-1]
    path = os.path.join(settings.MEDIA_URL ,"students",str(uuid.uuid4()) + img_extension)
    return default_storage.save(path, img)



class Image(APIView):

    def post(self, request, *args, **kwargs):

        upload_image(request=request)

        return Response({"success":"accepted"}, status=status.HTTP_202_ACCEPTED)