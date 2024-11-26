"""
URL configuration for authentication project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views, remote_login


urlpatterns = [
    # path('', views.home_view.as_view(), name='home'),
    path('home/', views.home_view.as_view(), name='home'),
    path('', views.login_view.as_view(), name='login'),
    path('matches/<str:username>', views.matches, name='login'),
    path('logout/', views.logout_view.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(),name = 'register'),
    path('login/42/', views.login_with_42, name='login_with_42'),
    path('login/42/callback/', remote_login.callback_with_42, name='callback_with_42'),
    path('profile/',views.profile.as_view(),name = 'profile'),
    path('forgot/',views.forgot_passwd,name = 'forget_passwd'),
    path('users/',views.get_all_users,name='users_profile'),
    path('users/<str:username>',views.users.as_view(),name='users_profile'),
    path('reset/<str:token>',views.reset_password ,name='reset pasword'),
    path('psswd/<str:username>',views.change_passwrd ,name='reset pasword'),
    path('send/<str:username>',views.send_friend_request,name='request'),
    path('accept/<str:username>',views.accept_friend_request,name='request'),
    path('reject/<str:username>',views.reject_friend_request,name='request'),
    path('friends/',views.get_friends ,name='friend list'),
    path('online/',views.get_online_friends ,name='friend list'),
    path('2fa/',views.generate_OTP.as_view() ,name='2fa'),
    
]

