from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Budget, Expense

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
            return redirect('budget_config')
    else:
        form = AuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})

@login_required
def budget_view(request):
    budget_obj, created = Budget.objects.get_or_create(user=request.user)

    # Fetch all recent expenses logged by this user
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')

    if request.method == 'POST':
        # Check if they are updating their budget
        if 'total_budget' in request.POST:
            new_budget = request.POST.get('total_budget')
            if new_budget:
                budget_obj.total_budget = new_budget
                budget_obj.save()

        # Check if they are logging a new expense
        elif 'amount' in request.POST:
            amount = request.POST.get('amount')
            category = request.POST.get('category')
            date = request.POST.get('date')
            description = request.POST.get('description', '')

            if amount and category and date:
                Expense.objects.create(
                    user=request.user,
                    amount=amount,
                    category=category,
                    date=date,
                    description=description
                )
        return redirect('budget_config')

    return render(request, 'authentication/budget.html', {
        'budget': budget_obj,
        'expenses': recent_expenses
    })
