from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('firebase-auth/', views.firebase_auth, name='firebase_auth'),
    path('logout/', views.logout_view, name='logout'),
]
