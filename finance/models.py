from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# 1. Kategoriya modeli (Masalan: Ovqat, Transport, Oylik va h.k.)
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


# 2. Kirim-Chiqim (Tranzaksiya) modeli
class Transaction(models.Model):
    # Kirim yoki Chiqim tanlovi
    TYPES = (
        ('IN', 'Kirim'),
        ('OUT', 'Chiqim')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategoriya")
    title = models.CharField(max_length=200, blank=True, verbose_name="Sarlavha")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Summa")
    type = models.CharField(max_length=3, choices=TYPES, verbose_name="Turi")
    date = models.DateField(default=timezone.now, verbose_name="Sana")
    time = models.TimeField(auto_now_add=True, null=True, verbose_name="Vaqt")
    note = models.TextField(blank=True, verbose_name="Izoh")


    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} ({self.date})"

    class Meta:
        verbose_name = "Amaliyot"
        verbose_name_plural = "Amaliyotlar"


# 3. Jamg'arma Maqsadlari (Kopilka) modeli
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    name = models.CharField(max_length=100, verbose_name="Maqsad nomi")  # Masalan: Mashina uchun
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Maqsad qilingan summa")
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Yig'ilgan summa")

    def __str__(self):
        return self.name

    # Maqsadga necha foiz yetganini hisoblash funksiyasi
    def progress_percentage(self):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 1)
        return 0

    class Meta:
        verbose_name = "Jamg'arma maqsadi"
        verbose_name_plural = "Jamg'arma maqsadlari"