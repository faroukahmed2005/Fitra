from django.urls import path
from .views import register, activate_account

app_name = 'members'

urlpatterns = [
    path('',register, name='register'),
    path('activate/<str:token>/',activate_account, name='activate'),
]