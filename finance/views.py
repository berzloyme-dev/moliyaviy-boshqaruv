from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
import calendar
from .models import Category, Transaction, SavingsGoal
from .forms import TransactionForm


# --- AVTORIZATSIYA BO'LIMI ---

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'logout.html')


# --- ASOSIY MANTIQ BO'LIMI ---

@login_required
def dashboard(request):
    user = request.user

    # Kirim va Chiqimlarni hisoblash
    total_in = Transaction.objects.filter(user=user, type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
    total_out = Transaction.objects.filter(user=user, type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_in - total_out

    # Bugungi statistika
    today = datetime.now().date()
    today_in = Transaction.objects.filter(user=user, type='IN', date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    today_out = Transaction.objects.filter(user=user, type='OUT', date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    today_balance = today_in - today_out

    # Oxirgi 5 ta amal (eng yangi birinchi)
    recent_transactions = Transaction.objects.filter(user=user).order_by('-time')[:5]

    # Kalendar uchun ma'lumotlar
    current_year = today.year
    current_month_num = today.month
    
    month_names = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
    current_month = f"{month_names[current_month_num - 1]} {current_year}"
    
    first_day = datetime(current_year, current_month_num, 1).date()
    weekday = first_day.weekday()
    empty_days_count = (weekday + 1) % 7
    empty_days = range(empty_days_count)
    
    days_in_month = calendar.monthrange(current_year, current_month_num)[1]
    
    calendar_days = []
    for day_num in range(1, days_in_month + 1):
        day_date = datetime(current_year, current_month_num, day_num).date()
        
        day_in = Transaction.objects.filter(user=user, type='IN', date=day_date).aggregate(Sum('amount'))['amount__sum'] or 0
        day_out = Transaction.objects.filter(user=user, type='OUT', date=day_date).aggregate(Sum('amount'))['amount__sum'] or 0
        day_balance = day_in - day_out
        
        calendar_days.append({
            'day': day_num,
            'date': day_date,
            'balance': day_balance,
            'has_data': day_in > 0 or day_out > 0,
            'is_today': day_date == today,
        })

    context = {
        'total_in': total_in,
        'total_out': total_out,
        'balance': balance,
        'today_in': today_in,
        'today_out': today_out,
        'today_balance': today_balance,
        'recent_transactions': recent_transactions,
        'calendar_days': calendar_days,
        'empty_days': empty_days,
        'current_month': current_month,
    }
    return render(request, 'dashboard.html', context)


@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(user=request.user, name=name)
            return redirect('add_transaction')
    return render(request, 'add_category.html')


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.date = datetime.now().date()
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'add_transaction.html', {'form': form})


@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    return redirect('all_transactions')


@login_required
def all_transactions(request):
    user = request.user
    filter_type = request.GET.get('type', 'all')
    selected_date_str = request.GET.get('date')
    
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except:
            selected_date = None
    else:
        selected_date = None
    
    transactions = Transaction.objects.filter(user=user).select_related('category')
    
    if selected_date:
        transactions = transactions.filter(date=selected_date)
    
    if filter_type == 'in':
        transactions = transactions.filter(type='IN')
    elif filter_type == 'out':
        transactions = transactions.filter(type='OUT')
    
    transactions = transactions.order_by('-time', '-date')
    
    if filter_type == 'in':
        total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        is_negative = False
    elif filter_type == 'out':
        total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        is_negative = True
    else:
        if selected_date:
            total_in = Transaction.objects.filter(user=user, type='IN', date=selected_date).aggregate(Sum('amount'))['amount__sum'] or 0
            total_out = Transaction.objects.filter(user=user, type='OUT', date=selected_date).aggregate(Sum('amount'))['amount__sum'] or 0
        else:
            total_in = Transaction.objects.filter(user=user, type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
            total_out = Transaction.objects.filter(user=user, type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
        total = total_in - total_out
        is_negative = total < 0
    
    today = datetime.now().date()
    current_year = today.year
    current_month_num = today.month
    
    month_names = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
    current_month = f"{month_names[current_month_num - 1]} {current_year}"
    
    first_day = datetime(current_year, current_month_num, 1).date()
    weekday = first_day.weekday()
    empty_days_count = (weekday + 1) % 7
    empty_days = range(empty_days_count)
    
    days_in_month = calendar.monthrange(current_year, current_month_num)[1]
    
    calendar_days = []
    for day_num in range(1, days_in_month + 1):
        day_date = datetime(current_year, current_month_num, day_num).date()
        
        day_in = Transaction.objects.filter(user=user, type='IN', date=day_date).aggregate(Sum('amount'))['amount__sum'] or 0
        day_out = Transaction.objects.filter(user=user, type='OUT', date=day_date).aggregate(Sum('amount'))['amount__sum'] or 0
        day_balance = day_in - day_out
        
        calendar_days.append({
            'day': day_num,
            'date': day_date,
            'balance': day_balance,
            'has_data': day_in > 0 or day_out > 0,
            'is_today': day_date == today,
            'is_selected': day_date == selected_date if selected_date else False,
        })
    
    context = {
        'transactions': transactions,
        'filter_type': filter_type,
        'total': abs(total),
        'is_negative': is_negative,
        'selected_date': selected_date,
        'calendar_days': calendar_days,
        'empty_days': empty_days,
        'current_month': current_month,
    }
    
    return render(request, 'all_transactions.html', context)



# Statistika sahifasi
@login_required
def statistics(request):
    user = request.user
    
    # Umumiy statistika
    total_in = Transaction.objects.filter(user=user, type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
    total_out = Transaction.objects.filter(user=user, type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_in - total_out
    
    # Kategoriya bo'yicha chiqimlar (title bo'yicha)
    expenses_by_title = Transaction.objects.filter(user=user, type='OUT').values('title').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]  # Top 10 ta ko'p xarajat qilingan
    
    # Kategoriya bo'yicha kirimlar
    income_by_title = Transaction.objects.filter(user=user, type='IN').values('title').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]
    
    # Oxirgi 30 kunlik statistika
    from datetime import timedelta
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    recent_expenses = Transaction.objects.filter(
        user=user, 
        type='OUT',
        date__gte=thirty_days_ago
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_income = Transaction.objects.filter(
        user=user,
        type='IN', 
        date__gte=thirty_days_ago
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Eng ko'p xarajat qilingan kun
    top_expense_day = Transaction.objects.filter(user=user, type='OUT').values('date').annotate(
        total=Sum('amount')
    ).order_by('-total').first()
    
    context = {
        'total_in': total_in,
        'total_out': total_out,
        'balance': balance,
        'expenses_by_title': expenses_by_title,
        'income_by_title': income_by_title,
        'recent_expenses': recent_expenses,
        'recent_income': recent_income,
        'top_expense_day': top_expense_day,
    }
    
    return render(request, 'statistics.html', context)


@login_required
def savings_calculator(request):
    """Jamg'arma kalkulyatori"""
    return render(request, 'savings_calculator.html')


@login_required
def adjust_balance(request):
    """Balansni o'zgartirish - farqni 'Boshqa chiqimlar' sifatida saqlash"""
    if request.method == 'POST':
        user = request.user
        new_balance = Decimal(request.POST.get('new_balance', 0))
        
        # Joriy balansni hisoblash
        total_in = Transaction.objects.filter(user=user, type='IN').aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        total_out = Transaction.objects.filter(user=user, type='OUT').aggregate(Sum('amount'))['amount__sum'] or Decimal(0)
        current_balance = total_in - total_out
        
        # Farqni hisoblash
        difference = current_balance - new_balance
        
        if difference > 0:
            # Balans kamaygan - chiqim qo'shamiz
            Transaction.objects.create(
                user=user,
                title='📝 Boshqa chiqimlar',
                amount=difference,
                type='OUT',
                date=datetime.now().date(),
                note='Balans o\'zgartirildi'
            )
        elif difference < 0:
            # Balans oshgan - kirim qo'shamiz
            Transaction.objects.create(
                user=user,
                title='📝 Boshqa kirimlar',
                amount=abs(difference),
                type='IN',
                date=datetime.now().date(),
                note='Balans o\'zgartirildi'
            )
        
        return redirect('dashboard')
    
    return redirect('dashboard')

