from django.urls import path , include 
from abscence.views import StudentViewSet , upload , Image ,  getAbsence

urlpatterns = [

path('image/', Image.as_view()),
path('upload/', upload),
path('getAbsenceInSingleCourse/',getAbsence )

]