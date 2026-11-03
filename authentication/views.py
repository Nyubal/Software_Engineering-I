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
# 📊 UPGRADED FINANCIAL DASHBOARD + ANALYTICS
# ==========================================

@login_required
def budget_view(request):
    budget_obj, created = Budget.objects.get_or_create(user=request.user)
    
    # 📥 Handle Incoming Data Updates (Forms)
    if request.method == 'POST':
        if 'total_budget' in request.POST:
            new_budget = request.POST.get('total_budget')
            if new_budget:
                budget_obj.total_budget = new_budget
                budget_obj.save()
        
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

    # 📊 Category Analytics Breakdown Calculation
    categories = ['Food', 'Rent', 'Entertainment', 'Utilities', 'Other']
    analytics_breakdown = []
    
    for cat in categories:
        cat_total = all_expenses.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or 0
        percentage = 0
        if total_spent > 0:
            percentage = round((float(cat_total) / float(total_spent)) * 100, 1)
        
        analytics_breakdown.append({
            'name': cat,
            'total': cat_total,
            'percentage': percentage
        })

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
        'analytics_breakdown': analytics_breakdown,
    })
import csv
from django.http import HttpResponse

@login_required
def export_expenses_csv(request):
    # 📜 Fetch all transaction log entries belonging to this user
    user_expenses = Expense.objects.filter(user=request.user).order_by('-date')

    # 📁 Configure the browser response header stream for a CSV file attachment
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="spendwise_expenses.csv"'

    # ✒️ Initialize the spreadsheet line writer
    writer = csv.writer(response)
    
    # Write the spreadsheet structural header column labels
    writer.writerow(['Execution Date', 'Classification Category', 'Description Details', 'Amount Subtotal'])

    # Write each individual transaction ledger item row line
    for expense in user_expenses:
        writer.writerow([expense.date, expense.category, expense.description, expense.amount])

    return response

