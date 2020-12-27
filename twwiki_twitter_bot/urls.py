from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.testView, name='testView'),
    path('', views.nada, name='nada'),
    path('pullTweets/', views.pullTweets, name='pullTweets')
]