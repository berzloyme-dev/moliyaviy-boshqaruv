from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Category, Transaction, SavingsGoal
from .forms import TransactionForm


# --- AVTORIZATSIYA BO'LIMI ---

# Ro'yxatdan o'tish
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


# Tizimga kirish
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


# Tizimdan chiqish
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    # GET request bo'lsa, tasdiqlash sahifasini ko'rsatamiz
    return render(request, 'logout.html')


# --- ASOSIY MANTIQ BO'LIMI ---

# Asosiy sahifa (Dashboard)
@login_required
def dashboard(request):
    user = request.user

    # Kirim va Chiqimlarni hisoblash (Faqat shu foydalanuvchi uchun)
    total_in = Transaction.objects.filter(user=user, type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
    total_out = Transaction.objects.filter(user=user, type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_in - total_out

    # Oxirgi 10 ta amaliyot
    latest_transactions = Transaction.objects.filter(user=user).select_related('category').order_by('-date')[:10]

    context = {
        'total_in': total_in,
        'total_out': total_out,
        'balance': balance,
        'latest_transactions': latest_transactions,
    }
    return render(request, 'dashboard.html', context)


# Kategoriya qo'shish
@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(user=request.user, name=name)
            return redirect('add_transaction')
    return render(request, 'add_category.html')


# Amaliyot (Kirim/Chiqim) qo'shish
@login_required
def add_transaction(request):
    if request.method == 'POST':
        # Formaga request.user ni yuboramiz (faqat o'z kategoriyalarini ko'rishi uchun)
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'add_transaction.html', {'form': form})


# O'chirish funksiyasi (Bonus)
@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    return redirect('all_transactions')

# Barcha amallar sahifasi (Filter bilan)
@login_required
def all_transactions(request):
    user = request.user
    filter_type = request.GET.get('type')

    transactions = Transaction.objects.filter(user=user).select_related('category')

    # Filter
    if filter_type == 'in':
        transactions = transactions.filter(type='IN')
    elif filter_type == 'out':
        transactions = transactions.filter(type='OUT')

    transactions = transactions.order_by('-date')

    # Hisob-kitob - Kirimdan chiqimni ayiramiz
    if filter_type == 'in':
        # Faqat kirimlar
        total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        is_negative = False
    elif filter_type == 'out':
        # Faqat chiqimlar (manfiy ko'rsatish uchun)
        total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        is_negative = True
    else:
        # Hammasi - kirimdan chiqimni ayiramiz
        total_in = Transaction.objects.filter(user=user, type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
        total_out = Transaction.objects.filter(user=user, type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
        total = total_in - total_out
        is_negative = total < 0

    context = {
        'transactions': transactions,
        'filter_type': filter_type,
        'total': abs(total),
        'is_negative': is_negative,
    }

    return render(request, 'all_transactions.html', context)