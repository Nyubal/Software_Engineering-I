from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('login')
    else:
        form = AuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Budget

@login_required
def budget_view(request):
    # Retrieve the user's existing budget or initialize a default entry
    budget_obj, created = Budget.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        new_budget = request.POST.get('total_budget')
        if new_budget:
            budget_obj.total_budget = new_budget
            budget_obj.save()
            return redirect('budget_config')

    return render(request, 'authentication/budget.html', {'budget': budget_obj})
