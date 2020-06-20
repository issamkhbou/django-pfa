from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=50)
    cin = models.IntegerField()
    email = models.EmailField(max_length=254) 
    classe = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    #imagePath = models.CharField(max_length=50,default="default.jpg")
    image = models.ImageField(upload_to = 'students')
    #imageBase64 = models.CharField(max_length=5000,default = "" , null =True )

    def __str__ (self) : 
        return self.name

    def equals (self,otherStudent) : 
        return  self.id == otherStudent.id 

    def exists (self , studentList) : 
        for s in studentList : 
            if self.equals(s) : 
                return True 
        return False 