from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def signup_view(request):
    if request.user.is_authenticated:
        if request.user.user_role == 'STAFF':
            return redirect('staff-dashboard')
        elif request.user.user_role == 'RIDER':
            return redirect('rider-dashboard')
        else:
            return redirect('customer-dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')

            # Redirect based on user role
            if user.user_role == 'RIDER':
                return redirect('rider-dashboard')
            else:
                return redirect('customer-dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

@csrf_protect
def signin_view(request):
    if request.user.is_authenticated:
        if request.user.user_role == 'STAFF':
            return redirect('staff-dashboard')
        elif request.user.user_role == 'RIDER':
            return redirect('rider-dashboard')
        else:
            return redirect('customer-dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')

                # Redirect based on user role
                if user.user_role == 'STAFF':
                    return redirect('staff-dashboard')
                elif user.user_role == 'RIDER':
                    return redirect('rider-dashboard')
                else:
                    return redirect('customer-dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/signin.html', {'form': form})

@login_required
def signout_view(request):
    logout(request)
    messages.success(request, 'Successfully signed out!')
    return redirect('signin')
