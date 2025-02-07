from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)  # Corrected
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    request.session.flush()  # Ensure all session data is cleared
    logout(request)
    return redirect('home')

def messages_page(request):
    return render(request, 'messages.html')