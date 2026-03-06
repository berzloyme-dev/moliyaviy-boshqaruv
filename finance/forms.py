from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Title uchun stil
        self.fields['title'].widget.attrs.update({
            'class': 'w-full px-5 py-4 text-lg bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-white/50 focus:border-white/50 outline-none transition backdrop-blur',
            'placeholder': 'Masalan: Ovqat, Transport, Oylik'
        })
        
        # Amount uchun stil
        self.fields['amount'].widget.attrs.update({
            'class': 'w-full px-5 py-4 text-lg bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-white/50 focus:border-white/50 outline-none transition backdrop-blur',
            'placeholder': '0'
        })
        
        # Note uchun stil
        self.fields['note'].widget.attrs.update({
            'class': 'w-full px-5 py-4 text-lg bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-white/50 focus:border-white/50 outline-none transition backdrop-blur',
            'rows': 3,
            'placeholder': 'Qo\'shimcha ma\'lumot (ixtiyoriy)'
        })

    class Meta:
        model = Transaction
        fields = ['title', 'type', 'amount', 'note']
