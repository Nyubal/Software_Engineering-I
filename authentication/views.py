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
# 📊 FINAL BUDGET + MULTI-CURRENCY DASHBOARD
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

    # 🔍 Handle Category Filters & Sorting Toggles via URL Parameters
    selected_category = request.GET.get('category_filter', 'All')
    selected_sort = request.GET.get('sort_by', 'newest')
    
    # 💱 NEW: Intercept Multi-Currency URL State Parameters
    currency_selection = request.GET.get('currency', 'USD')
    
    all_expenses = Expense.objects.filter(user=request.user)
    total_spent_usd = all_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_balance_usd = float(budget_obj.total_budget) - float(total_spent_usd)

    # ⚠️ Visual Warning Threshold Validation (Trigger alert at >= 80% usage)
    warning_threshold = float(budget_obj.total_budget) * 0.80
    trigger_warning = float(total_spent_usd) >= warning_threshold

    # 💶 Static Multi-Currency Converter Valuation Calculation Logic
    conversion_rates = {
        'USD': {'symbol': '$', 'rate': 1.0},
        'EUR': {'symbol': '€', 'rate': 0.92},
        'GBP': {'symbol': '£', 'rate': 0.77}
    }
    
    selected_meta = conversion_rates.get(currency_selection, conversion_rates['USD'])
    currency_symbol = selected_meta['symbol']
    rate = selected_meta['rate']

    # Convert Core Analytics Metric Aggregations
    converted_budget = round(float(budget_obj.total_budget) * rate, 2)
    converted_spent = round(float(total_spent_usd) * rate, 2)
    converted_balance = round(float(remaining_balance_usd) * rate, 2)

    # 📊 Category Analytics Breakdown Calculation
    categories = ['Food', 'Rent', 'Entertainment', 'Utilities', 'Other']
    analytics_breakdown = []
    for cat in categories:
        cat_total_usd = all_expenses.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or 0
        cat_total_converted = round(float(cat_total_usd) * rate, 2)
        percentage = 0
        if total_spent_usd > 0:
            percentage = round((float(cat_total_usd) / float(total_spent_usd)) * 100, 1)
        analytics_breakdown.append({
            'name': cat, 
            'total': cat_total_converted, 
            'percentage': percentage
        })

    # 📜 Filter Ledger Entries based on Selection
    if selected_category != 'All':
        displayed_expenses = all_expenses.filter(category=selected_category)
    else:
        displayed_expenses = all_expenses

    if selected_sort == 'amount_desc':
        displayed_expenses = displayed_expenses.order_by('-amount')
    elif selected_sort == 'amount_asc':
        displayed_expenses = displayed_expenses.order_by('amount')
    elif selected_sort == 'oldest':
        displayed_expenses = displayed_expenses.order_by('date')
    else:
        displayed_expenses = displayed_expenses.order_by('-date')

    return render(request, 'authentication/budget.html', {
        'budget': budget_obj,
        'expenses': displayed_expenses,
        'total_spent': converted_spent,
        'remaining_balance': converted_balance,
        'converted_budget': converted_budget,
        'trigger_warning': trigger_warning,
        'selected_category': selected_category,
        'selected_sort': selected_sort,
        'analytics_breakdown': analytics_breakdown,
        'currency_selection': currency_selection,
        'currency_symbol': currency_symbol,
    })

# ==========================================
# 📥 DATA EXPORT GENERATION UTILITY
# ==========================================
import csv
from django.http import HttpResponse

@login_required
def export_expenses_csv(request):
    user_expenses = Expense.objects.filter(user=request.user).order_by('-date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="spendwise_expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Execution Date', 'Classification Category', 'Description Details', 'Amount Subtotal'])
    for expense in user_expenses:
        writer.writerow([expense.date, expense.category, expense.description, expense.amount])
    return response
