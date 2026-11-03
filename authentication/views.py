from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Budget, Expense

# ==========================================
# 🔐 USER AUTHENTICATION MODULES
# ==========================================

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

# ==========================================
# 📊 UPGRADED FINANCIAL DASHBOARD MODULE
# ==========================================

@login_required
def budget_view(request):
    budget_obj, created = Budget.objects.get_or_create(user=request.user)
    
    # 📥 Handle Incoming Data Updates (Forms)
    if request.method == 'POST':
        # Condition A: Modifying spending boundary limits
        if 'total_budget' in request.POST:
            new_budget = request.POST.get('total_budget')
            if new_budget:
                budget_obj.total_budget = new_budget
                budget_obj.save()
        
        # Condition B: Submitting a new line-item expense
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

    # 🔍 Handle Category Filters via URL Parameters
    selected_category = request.GET.get('category_filter', 'All')
    all_expenses = Expense.objects.filter(user=request.user)

    # 🧮 Financial Summary Calculations
    total_spent = all_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_balance = float(budget_obj.total_budget) - float(total_spent)

    # ⚠️ Visual Warning Threshold Validation (Trigger alert at >= 80% usage)
    warning_threshold = float(budget_obj.total_budget) * 0.80
    trigger_warning = float(total_spent) >= warning_threshold

    # 📜 Filter Ledger Entries for Table View Display
    if selected_category != 'All':
        displayed_expenses = all_expenses.filter(category=selected_category).order_by('-date')
    else:
        displayed_expenses = all_expenses.order_by('-date')

    return render(request, 'authentication/budget.html', {
        'budget': budget_obj,
        'expenses': displayed_expenses,
        'total_spent': total_spent,
        'remaining_balance': remaining_balance,
        'trigger_warning': trigger_warning,
        'selected_category': selected_category,
    })
