from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import UserToken
from django.utils import timezone
from django.urls import reverse
import resend
import threading
from django.conf import settings


resend.api_key = getattr(settings, 'SENSITIVE_VARIABLE', None)
def send_email_async(email_data):
    # Send the email using the resend module
    resend.Emails.send(email_data)

def send_confirmation_email(request, user):
    # Generate a random token
    token = get_random_string(length=32)
    
    # Create a UserToken instance
    user_token = UserToken.objects.create(
        user=user,
        token=token,
        token_type='email_confirmation',
        
    )
    
    # Compose the email message
    recipient = user.email
    confirmation_link = f'https://fidelefinance.com/confirm-email/{token}/'
    print(confirmation_link)
    email_data = {
                "from": "fidelefinance <noreply@fidelefinance.com>",
                "to": recipient,
                "subject": "Confirm your email address",
                "html": f"""
                    <!DOCTYPE html>
                    <html lang="en">
                   
                    <body>
                        <div class="container">
                            <td align="center" valign="top" bgcolor="#ffffff" style="border-radius:5px;border-left:1px solid #e0bce7;border-top:1px solid #e0bce7;border-right:1px solid #efefef;border-bottom:1px solid #efefef">
        <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0">
          <tbody>
            <tr>
              <td valign="top" align="center" style="font-family:Google Sans,Roboto,Helvetica,Arial sans-serif;font-size:36px;font-weight:500;line-height:44px;color:#202124;padding:40px 40px 0px 40px;letter-spacing:-0.31px">
              <img src="https://fidelefinance.com/static/assets/logo/bluelogo.png" style="border-radius: 15px;" height="200"/>
                </td>
            </tr>
            
            <tr>
              <td valign="top" align="center" style="font-family:Google Sans,Roboto,Helvetica,Arial sans-serif;font-size:14px;font-weight:500;height:44px;color:#202124;padding:40px 40px 0px 40px;letter-spacing:-0.31px">
              
                Hi <span class="il">{user.username}</span>!</td>
            </tr>
            

            
            <tr>
              <td valign="top" align="left" style="font-family:Roboto,Helvetica,Arial sans-serif;font-size:14px;line-height:24px;color:#414347;padding:40px 40px 20px 40px">
              Thanks for signing up for <span class="il">FideleFinance! </span><br> We're so excited to have you onboard.</td>
            </tr>
            <tr>
              <td valign="top" align="left" style="font-family:Roboto,Helvetica,Arial sans-serif;font-size:14px;line-height:24px;color:#414347;padding:40px 40px 20px 40px">
              Please click on this link {confirmation_link} to confirm your email.</td>
            </tr>



        
            <tr>
              <td valign="top" align="cenetr" style="font-family:Roboto,Helvetica,Arial sans-serif;font-size:14px;line-height:24px;color:#414347;padding:20px 20px 0px 40px">
                Thanks for registering! <br>
                If you did not sign up for an account with us, please ignore this email. </td>
            </tr>
            <tr>
              <td valign="top" align="center" style="font-family:Roboto,Helvetica,Arial sans-serif;font-size:14px;line-height:24px;color:#414347;padding:10px 40px 40px 40px">
                <a href="https://fidelefinance.com">fidelefinance.com</a></td>
            </tr>
            
          </tbody>
        </table>
      </td>
                        </div>
                    </body>
                    </html>
                """,
            }

            # Create a thread to send the email asynchronously
    email_thread = threading.Thread(target=send_email_async, args=(email_data,))
    email_thread.start()

    
    return JsonResponse({'success': True, 'message': f"Confirmation email sent successfully"})



def confirm_email(request, token):
    try:
        user_token = UserToken.objects.get(token=token, token_type='email_confirmation', used=False)
    except UserToken.DoesNotExist:
        # Token not found 
        return redirect('userauths:email_invalid')
    
    # Check if the token has expired
    if user_token.expires_at < timezone.now():
        # Token has expired
        return redirect('userauths:email_invalid')
    
    # Mark the token as used
    user_token.used = True
    user_token.save()
    
    # Update the user's email_verified field
    user = user_token.user
    user.is_email_verified = True
    user.save()
    user_token.delete()
    
    return redirect('userauths:email_confirmed')  # Redirect to a page indicating that the email has been confirmed


def reset_password(request, user):
    cooldown_period = timezone.timedelta(minutes=1)  # Adjust cooldown period as needed
    now = timezone.now()
    # Generate a random token
    if user.last_password_reset_request and user.last_password_reset_request + cooldown_period > now:
      return redirect('userauths:password_reset_cooldown')
    token = get_random_string(length=32)
    
    # Create a UserToken instance
    user_token = UserToken.objects.create(
        user=user,
        token=token,
        token_type='password_reset',
        expires_at=timezone.now() + timezone.timedelta(minutes=30)
    )
    
    # Compose the email message
    recipient = user.email
    reset_link = f'https://fidelefinance.com/reset-password/{token}/'
    email_data = {
                "from": "FideleFinance <noreply@fidelefinance.com>",
                "to": recipient,
                "subject": "FORGOT PASSWORD",
                "html": f"""
                    <!DOCTYPE html>
                    <html lang="en">
                   
                    <body>
                        <div class="container">
                            <td align="center" valign="top" bgcolor="#ffffff" style="border-radius:5px;border-left:1px solid #e0bce7;border-top:1px solid #e0bce7;border-right:1px solid #efefef;border-bottom:1px solid #efefef">
        <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0">
          <tbody>
            <tr>
              <td valign="top" align="center" style="font-family:Google Sans,Roboto,Helvetica,Arial sans-serif;font-size:36px;font-weight:500;line-height:44px;color:#202124;padding:40px 40px 0px 40px;letter-spacing:-0.31px">
              <img src="https://fidelefinance.com/static/assets/logo/bluelogo.png" style="border-radius: 15px;" height="200"/>
                </td>
            </tr>
            
            <tr>
              <td valign="top" align="center" style="font-family:Google Sans,Roboto,Helvetica,Arial sans-serif;font-size:14px;font-weight:500;height:44px;color:#202124;padding:40px 40px 0px 40px;letter-spacing:-0.31px">
              
                <h2>Hi <span class="il">{user.username}</span>!</h2></td>
            </tr>
            

            
            <tr>
              <td valign="top" align="left" style="font-family:Roboto,Helvetica,Arial sans-serif;font-size:14px;line-height:24px;color:#414347;padding:40px 40px 20px 40px">
              You requested a password reset on your<br> FideleFinance account.</td>
            </tr>
            <tr>
              <td valign="top" align="left" style="font-family:Roboto,Helvetica,Arial sans-serif;font-size:14px;line-height:24px;color:#414347;padding:40px 40px 20px 40px">
              Please click on this link {reset_link}<br> to reset your password, and set a new password on your account.</td>
            </tr>



        
            <tr>
              <td valign="top" align="cenetr" style="font-family:Roboto,Helvetica,Arial sans-serif;font-size:14px;line-height:24px;color:#414347;padding:20px 20px 0px 40px">
              
                If you did not initialize this request, please ignore this email. </td>
            </tr>
            <tr>
              <td valign="top" align="center" style="font-family:Roboto,Helvetica,Arial sans-serif;font-size:14px;line-height:24px;color:#414347;padding:10px 40px 40px 40px">
                <a href="https://fidelefinance.com">fidelefinance.com</a></td>
            </tr>
            
          </tbody>
        </table>
      </td>
                        </div>
                    </body>
                    </html>
                """,
            }

            # Create a thread to send the email asynchronously
    email_thread = threading.Thread(target=send_email_async, args=(email_data,))
    email_thread.start()
    user.last_password_reset_request = now
    user.save()
    
    return JsonResponse({'success': True, 'message': f"Password reset email sent successfully"})


