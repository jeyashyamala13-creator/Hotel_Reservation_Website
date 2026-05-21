from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from .forms import CustomRegistrationForm, CustomLoginForm

class RegisterView(View):
    def get(self, request):
        form = CustomRegistrationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Register pannathum auto-login aagidum
            messages.success(request, f"Welcome {user.username}! Account created successfully.")
            return redirect('hotel_list')
        return render(request, 'users/register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        form = CustomLoginForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('hotel_list')
        messages.error(request, "Invalid username or password.")
        return render(request, 'users/login.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('hotel_list')

from django.contrib.auth import login # Intha line-ah import pannunga
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

class RoleBasedLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        # 1. Login panna user-ah get pannuvom
        user = form.get_user()
        
        # 2. Login-ah explicit-ah perform pannuvom
        login(self.request, user)
        
        # 3. Print statement - Terminal-la varutha nu paarkka
        print(f"DEBUG: Logged in as {user.username}, Is Superuser: {user.is_superuser}")
        
        # 4. Redirect Logic
        if user.is_superuser:
            return redirect('custom_admin_dashboard')
        
        return redirect('user_dashboard')