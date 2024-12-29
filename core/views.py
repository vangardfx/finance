from django.shortcuts import render,redirect
import django
from django.contrib import messages
from .models import Plan, UserComplaints
from core.forms import ContactForm
from userauths.forms import TransactionForm, WithdrawForm, UserRegisterForm
from userauths.models import Transaction, Deposit, Withdraw, UserDevice
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from userauths.models import User
from django.contrib.auth import login, authenticate
from core.models import BtcAddress,EthAddress,OtherAddress
from django.http import JsonResponse
import resend
from django.db.models import Sum
from django.conf import settings
import json
from .names import names
from math import ceil
from django.views.decorators.http import require_http_methods
from .utils import get_device_info


resend.api_key = getattr(settings, 'SENSITIVE_VARIABLE', None)





def custom_error_page(request,exception):
    return render(request, 'errors/custom_error.html')
def custom_error_page2(request,exception):
    return render(request, 'errors/csrf_error.html')
def custom_error_page1(request):
    return render(request, 'errors/500.html')



def index(request):
    # last_plan = Plan.objects.last()
    
    # other_plans = Plan.objects.exclude(pk=last_plan.pk).order_by('id')
    plans = Plan.objects.all().order_by('id')
    names_json = json.dumps(names)
    context = {
        # "plans": other_plans,
        # "last_plan": last_plan,
        "plans": plans,
        "namesJson": names_json,
    }
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            request.session['pre_filled_email'] = email
            return redirect('userauths:sign-up')
    return render(request, "core/index.html",context)

def pricing(request):
    last_plan = Plan.objects.last()
    
    # Get the other three objects excluding the last one
    other_plans = Plan.objects.exclude(pk=last_plan.pk).order_by('id')
    context = {
        "plans": other_plans,
        "last_plan": last_plan,
    }
    return render(request,"core/pricing/index.html", context)
def services(request):
    return render(request,"services/index.html")

def about(request):
    return render(request,"about-us/index.html")


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Thanks, message sent succesfully")
           
    else:
        form = ContactForm()

    return render(request, 'contact/index.html', {'form': form})



@login_required
def dashboard_view(request):
    user = request.user
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')[:5]
    confirmed_deposits = Deposit.objects.filter(user=user, confirmed=True)
    total_deposit = confirmed_deposits.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    plans = Plan.objects.all().order_by('id')
    
    context = {
        "plans": plans,
        "total_deposit": total_deposit,
        'user_transactions': user_transactions,
    }
    
    return render(request, "core/dashboard-crypto.html", context)



@login_required
def profile_view(request):
    current_user = User.objects.get(id=request.user.id)
    form = UserRegisterForm(request.POST or None, instance=current_user)
    if form.is_valid():
        form.save()
        login(request, current_user)
        messages.success(request, "Profile updated successfully ")
        return redirect("core:dashboard")
    return render(request, "core/account-profile.html", {'form':form})

@login_required
def withdrawal_view(request):
    user_withdrawals = Withdraw.objects.filter(user=request.user).order_by('-timestamp')
    context = {'user_withdrawals': user_withdrawals}
    return render(request, "core/withdrawals.html", context)
@login_required
def profile_settings_view(request):
    current_user = User.objects.get(id=request.user.id)
    form = UserRegisterForm(request.POST or None, instance=current_user)
    if form.is_valid():
        form.save()
        login(request, current_user)
        messages.success(request, "Profile updated successfully ")
        return redirect("core:dashboard")
    
    return render(request, "core/pages-profile-settings.html", {'form':form})


@login_required
def plans_view(request):
    plans = Plan.objects.all().order_by('id')
    middle_index = ceil(len(plans) / 2)
    context = {
        "plans": plans,
        "middle_index": middle_index,
    }
    return render(request, "core/product-list.html", context)


def plan_detail_view(request, pid):
    if request.user.is_authenticated:
        form = TransactionForm()
        product = Plan.objects.get(pid=pid)
    
        context = {
            "form": form,
            "p": product,

        }
    
        return render(request, "core/product-detail.html", context)
    else:
        messages.warning(request, "Sign in to activate plan")
        return redirect("userauths:sign-in")

@login_required
def deposit_view(request):
    btc = BtcAddress.objects.all()
    eth = EthAddress.objects.all()
    other = OtherAddress.objects.all()
    context ={
        'btc': btc,
        'eth': eth,
        'other': other,
    }
    return render(request, "core/deposit.html",context)

@login_required
def send_deposit_review(request):
    user = request.user
    email = request.user.email
    amount = request.POST['deposit']
    wallet_address = request.POST['address']
    trx_hash=request.POST['trx_hash']
    review = Deposit.objects.create(
        user = user,
        amount = request.POST['deposit'],
        currency = request.POST['options'],
        wallet_address = request.POST['address'],
        trx_hash=request.POST['trx_hash'],
    )
    try:
        r = resend.Emails.send({
                    "from": "fidellefinance <noreply@fidellefinance.com>",
                    "to": 'support@fidelefinance.com',
                    "subject": f"{user} Deposited {amount}",
                    "html": f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <body>
                            <div class="container">
                                <h1>Hey Admin,<br> Someone created an account !</h1>
                                <p>{user} with email: {email} has deposited:.</p>
                                <h2>Amount: {amount}</h2>
                                <p>wallet address: {wallet_address}</p>
                                <p>Transaction Hash: {trx_hash}</p><br><br>
                                <div style="text-align: center; align-items: center;">
                                    <a href="https://fidellefinance.com/admin/userauths/deposit/" class="btn btn-primary" style="background-color: #007bff; font-size: 16px; border-color: #007bff; padding: 10px 20px; border-radius: 2px;" target="_blank">Admin Panel</a><br><br>
                                </div>
                                
                            </div>

                            
                        </body>
                        </html>
                    """,
                })
    except Exception as e:
          pass
    btc = BtcAddress.objects.all()
    eth = EthAddress.objects.all()
    other = OtherAddress.objects.all()
    context ={
        'btc': btc,
        'eth': eth,
        'other': other,
    }

    return render(request, "core/wallet-details.html", context)

@login_required
def referral_view(request):
    current_user = request.user
    current_user_referral_code = current_user.referral_code
    current_user_referrer_code = current_user.referred
    current_user_total_ref = current_user.ref_bonus

    # Count the number of users with the same referral code
    referred_users = User.objects.filter(referred=current_user_referral_code)
    referred_users_count = User.objects.filter(referred=current_user_referral_code).count()

    # Get the users who have the same referral code as the current user
    user_referrer = User.objects.filter(referral_code=current_user_referrer_code)

    

    context = {
        'current_user': current_user,
        'referred_users': referred_users,
        'referred_users_count': referred_users_count,
        'user_referrer': user_referrer,
        'current_user_total_ref': current_user_total_ref,
    }
    return render(request, "core/referrals.html", context)
@login_required
def send_payment_review(request, pid):
    user = request.user
    plan = Plan.objects.get(pid=pid)
    least_amount = plan.least_amount
    max_amount = plan.max_amount
    amount = Decimal(request.POST['amount'])
    if float(request.POST['amount'])  <= user.total_deposit:
        try:

            review = Transaction.objects.create(
                user = user,
                title = plan.title,
                interval = plan.interval,
                description = plan.description,
                percentage_return = plan.percentage_return,
                amount = amount,
                least_amount = least_amount,
                max_amount = max_amount,
            )
            try:
                r = resend.Emails.send({
                    "from": "fidellefinance <noreply@fidellefinance.com>",
                    "to": 'support@fidelefinance.com',
                    "subject": f"{user} made a transaction of {amount}",
                    "html": f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                    
                            
                        </head>
                        <body>
                            <div class="container">
                                <h1>Hey Admin,<br> Someone created an account !</h1>
                                <p>A {user} has made an investment .</p>
                                <h2>Amount: {amount}</h2>
                                <p>Plan: {plan}</p><br><br>
                                <div style="text-align: center; align-items: center;">
                                    <a href="https://fidellefinance.com/admin/userauths/deposit/" class="btn btn-primary" style="background-color: #007bff; font-size: 16px; border-color: #007bff; padding: 10px 20px; border-radius: 2px;" target="_blank">Admin Panel</a><br><br>
                                </div>
                                
                            </div>
                        </body>
                        </html>
                    """,
                })
            except Exception as e:
                pass
        except Exception as e:
            messages.error(request, f"An error occurred {e}")
            return redirect('core:dashboard')
    else:
        messages.warning(request,"Insufficient Balance, Please Deposit or Choose Another Plan")
        return redirect('core:deposit')
    date = review.timestamp
    tid = review.transaction_id
    context = {
        "amount":amount,
        "plan":plan,
        "date": date,
        "tid": tid,
    }

    return render(request,"core/deposit-success.html", context)

@login_required
def transaction_view(request):

    user_transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    context = {'user_transactions': user_transactions}
    return render(request, "core/transactions.html", context)


@login_required
def deposits_view(request):
    user = request.user
    user_deposits = Deposit.objects.filter(user=request.user).order_by('-timestamp')
    total_deposit = user.total_deposit if hasattr(user, 'total_deposit') else 0
    progress = min((total_deposit / 100000) * 100, 100)  # Ensure it doesn't exceed 100%
    context = {
        'user_deposits': user_deposits,
        'total_deposit': total_deposit,
        'progress': round(progress, 2)  # Round to 2 decimal places
    }
    return render(request, "core/deposits.html", context)

@login_required
def withdraw_view(request):
    user = request.user
    email = request.user.email
    if request.method == 'POST':
        currency = request.POST['options']
        wallet_address = request.POST['wallet_address']
        if float(request.POST['amount']) <= user.total_deposit:
            amount = Decimal(request.POST['amount'])
            review = Withdraw.objects.create(
                user = user,
                email = email,
                amount = amount,
                currency = currency,
                wallet_address = wallet_address,
            )
            messages.success(request,"Withdrawal placement pending")
            try:
                r = resend.Emails.send({
                "from": "fidellefinance <noreply@fidellefinance.com>",
                "to": 'support@fidelefinance.com',
                "subject": "Withdrawal Placement",
                "html": f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    
                    <body>
                        <div class="container">
                            <h1>Hey Admin,<br> Someone created an account !</h1>
                            <p>A user: {user} with email: {email} has placed a withdrawal of .</p>
                            <h2>{amount}</h2>
                            <p>Login to your admin panel to view them:</p><br><br>
                            <div style="text-align: center; align-items: center;">
                                <a href="https://fidellefinance.com/admin/userauths/withdraw/" class="btn btn-primary" style="background-color: #007bff; font-size: 16px; border-color: #007bff; padding: 10px 20px; border-radius: 2px;" target="_blank">Admin Panel</a><br><br>
                            </div>
                            
                        </div>

                    </body>
                    </html>
                """,
            })
            except Exception as e:
                pass
    
    
            return redirect('core:dashboard')

        else:
            messages.warning(request,"Insufficient Balance")
            return redirect('core:withdraw')
    else:
        form = WithdrawForm()
    context = {
        'form':form,
        'user': user
        }
    return render(request,"core/withdraw.html",context)

@login_required
def search_view(request):
    query = request.GET.get("search")

    plans = Plan.objects.filter(title__icontains=query).order_by("-date")
    transactions = Transaction.objects.filter(title__icontains=query).order_by("-timestamp")
    context={
        "plans": plans,
        "query": query,
        "transactions": transactions,
    }
    return render(request, "core/search.html", context)


def get_user_devices(request):
    devices = UserDevice.objects.filter(user=request.user).order_by('-last_login')[:5]
    data = [
        {
            "device_name": device.device_name,
            "ip_address": device.ip_address,
            "last_login": device.last_login.strftime('%Y-%m-%d %H:%M:%S'),
            "is_current": get_device_info(request) == device.device_name,
        }
        for device in devices
    ]
    return JsonResponse({"devices": data})


@login_required
@require_http_methods(["DELETE"])
def delete_device(request, device_id):
    try:
        # Ensure the device belongs to the logged-in user
        device = UserDevice.objects.get(id=device_id, user=request.user)
        device.delete()
        return JsonResponse({"success": True}, status=200)
    except UserDevice.DoesNotExist:
        return JsonResponse({"error": "Device not found"}, status=404)