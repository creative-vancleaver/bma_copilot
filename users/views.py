from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse


from .forms import UserRegistrationForm
from .models import User

def redirect_authenticated_user(user):
    # RETURNS FALSE IF USER IS LOGGED IN - TRIGGERING REDIRECT
    return not user.is_authenticated

@user_passes_test(redirect_authenticated_user, login_url='home')
def register_user(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save() # ENSURE CALLS create_user CUSTOM MANAGER
            user.set_password(form.cleaned_data['password']) # HASH PASSWORD
            user.save()
            login(request, user) # LOG USER IN AFTER REGISTRATION
            messages.success(request, "Registration success. Welcome!")
            return redirect('home')
        else:
            messages.error(request, "please correct the errors below.")
        
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', { "form": form })

@user_passes_test(redirect_authenticated_user, login_url='home')
def user_login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'core/login.html', {'form': {'errors': True}})

    return render(request, 'core/login.html')

