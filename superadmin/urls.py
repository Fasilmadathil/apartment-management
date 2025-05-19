from django.urls import path
from . import views
from .views import RegisterAPIView, LoginAPIView

urlpatterns = [
    # path('', views.home, name='home'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('add-user/', views.AddUserAPIView.as_view(), name='add_user'),

]
