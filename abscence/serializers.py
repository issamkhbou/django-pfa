from rest_framework import  serializers
from .models import * 
from drf_extra_fields.fields import Base64ImageField
import base64 



class StudentSerializer(serializers.ModelSerializer):
    image=Base64ImageField()
    
    imageBase64 = serializers.SerializerMethodField()
    def get_imageBase64(self, student):
        return  base64.b64encode(student.image.read()).decode("utf-8")    


    class Meta:
        model = Student
        #fields = ['id',"cin","name", 'email', 'password', 'classe']
        fields = "__all__"

    def create(self, validated_data):
        image=validated_data.pop('image')
        cin=validated_data.pop('cin')
        classe=validated_data.pop('classe')
        email=validated_data.pop('email')
        password=validated_data.pop('password')
        name=validated_data.pop('name')
        return Student.objects.create(name=name,image=image , cin = cin , classe = classe , email = email , password = password)
