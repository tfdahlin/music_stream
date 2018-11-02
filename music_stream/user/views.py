from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from main.logging import Log

# Create your views here.

def login(request):
    if request.method == 'GET':
        return render(request, 'user/index.html')
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password']
        user = authenticate(request, username=username, password=password1)
        if user is not None:
            logincontext = {}
            logincontext['username'] = username
            Log.logLogin(logincontext)
            auth_login(request, user)
            return redirect('main:index')
        else:
            print("Authentication failed")
            messages.error(request, 'Invalid login information.')
            return render(request, 'user/index.html')
    
def register(request):
    if request.method == 'GET':
        return render(request, 'user/register.html')
    
    if request.method == 'POST':
        username = request.POST['username']
        if username is None:
            return redirect('login:register')
        try:
            user = User.objects.get(username = username)
            print("User exists.")
            return redirect('login:register')
        except:
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if((username is None) or (password1 is None) or (password2 is None)):
                print("Field is 'None'")
                return redirect('login:register')
            
            if(password1 != password2):
                print("Passwords dont match")
                return redirect('login:register')
                
            user = User.objects.create_user(username=username, password=password1)
            user.username = username
            hashed_password = make_password(password=password1)
            user.password = hashed_password
            user.save()
            auth_login(request, user)
            return redirect('login:login')

@login_required(login_url="login:login")            
def logout_view(request):
    logoutcontext = {}
    logoutcontext['username'] = request.user.get_username()
    logout(request)
    Log.logLogout(logoutcontext)
    return redirect('main:index')