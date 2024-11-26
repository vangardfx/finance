import re
import hashlib
from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User,Transaction, Deposit,Withdraw
from .countries import sorted_countries
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal
import resend
from django.conf import settings


resend.api_key = getattr(settings, 'SENSITIVE_VARIABLE', None)
CURRENCY = (
    ("Bitcoin (BTC)", "Bitcoin (BTC)"),
    ("Ethereum (ETH)", "Ethereum (ETH)"),
    ("Tether (USDT)", "Tether (USDT)"),
)


def validate_referral_code(value):
    """
    Custom validator to check if the referral code exists in the User model.
    If it exists, create the account.
    If it doesn't exist, raise a ValidationError.
    """
    try:
        user = User.objects.get(referral_code=value)
        user.save()
        email = user.email
        username = user.username
        r = resend.Emails.send({
                "from": "fidelefinance <support@fidelefinance.com>",
                "to": email,
                "subject": f"You referred a new user",
                "html": f"""
                
                
                    <body>
                        <div class="container">
                            <h1>Hey {username},<br> you have referred a new user !</h1>
                            <p>Referral code: {value}.</p><br>
                            
                            <div style="text-align: center; align-items: center;">
                                <a href="https://fidelefinance.com/app/referrals" class="btn btn-primary" style="background-color: #007bff; font-size: 16px; border-color: #007bff; padding: 10px 20px; border-radius: 2px;" target="_blank">View Referrals</a><br><br>
                            </div>
                            
                        </div>

                    </body>
                    </html>
                """,
            })
  
    except User.DoesNotExist:
        raise ValidationError('This referral code does not exist.')

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username","class": "form-control"}))
    contact = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Phone Number","class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}))
    address = forms.ChoiceField(choices=sorted_countries, widget=forms.Select(attrs={"placeholder": "Country", "class": "form-control"}))
    btc_address = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "BTC address", "class": "form-control",}), required=False)
    eth_address = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "ETH address", "class": "form-control"}), required=False)
    usdt_address = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "USDT address", "class": "form-control",}), required=False)
    referred = forms.CharField(widget=forms.HiddenInput(attrs={"placeholder": "*Optional","class": "form-control",}),validators=[validate_referral_code], required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control","id":"password-field"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password", "class": "form-control","id":"password-field2"}))
    
    class Meta:
        model = User
        fields = ['username','contact','email','address','btc_address','eth_address','usdt_address','referred']

class TransactionForm(forms.ModelForm):
    user = forms.EmailField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control",'readonly': 'readonly'}))
    amount = forms.CharField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control"}))
    least_amount = forms.CharField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control",'readonly': 'readonly'}))
    max_amount = forms.CharField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control",'readonly': 'readonly'}))
    transaction_id= forms.CharField(initial='Default Value', widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control",'readonly': 'readonly'}))
    
    class Meta:
        model = Transaction
        fields = ['user','amount','least_amount','max_amount','transaction_id']


class DepositForm(forms.ModelForm):
    user = forms.EmailField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control",'readonly': 'readonly'}))
    currency = forms.ChoiceField(choices=CURRENCY, widget=forms.Select(attrs={"placeholder": "This question is about..", "class": "form-control","id":"card-holder-input"}))
    wallet_address = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Wallet Address", "class": "form-control","id":"card-holder-input","required":True}))
    amount = forms.CharField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control"}))
    
    class Meta:
        model = Deposit
        fields = ['user','amount','wallet_address','currency']

class WithdrawForm(forms.ModelForm):
    user = forms.CharField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "Username","class": "form-control"}))
    email = forms.EmailField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control",'readonly': 'readonly'}))
    amount = forms.CharField(initial='Default Value',widget=forms.TextInput(attrs={"placeholder": "", "class": "form-control"}))
    currency = forms.ChoiceField(choices=CURRENCY, widget=forms.Select(attrs={"placeholder": "This question is about..", "class": "form-control","id":"card-holder-input"}))
    wallet_address = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Wallet Address", "class": "form-control","id":"card-holder-input","required":True}))
    
    class Meta:
        model = Withdraw
        fields = ['user','email','amount','currency','wallet_address']
