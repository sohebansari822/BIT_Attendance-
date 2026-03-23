from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_page, name='register_page'),
    path('register/submit/', views.register_person, name='register_person'),
    path('recognize/', views.recognize_page, name='recognize_page'),
    path('recognize/submit/', views.recognize_face, name='recognize_face'),
    path('attendance/', views.attendance_list, name='attendance_list'),
]
