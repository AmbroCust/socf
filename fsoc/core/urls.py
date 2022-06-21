from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import home, profile, RegisterView, CustomLoginView
from .form import LoginForm

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='user-register'),
    path('profile/', profile, name='users-profile'),
    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True, template_name='login.html',
                                           authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
]