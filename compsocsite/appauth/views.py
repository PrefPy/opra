import datetime
import time

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.core import mail

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from polls.models import Message
from polls import opra_crypto
import cas.middleware

def register(request):
    context = RequestContext(request)
    
    registered = False
    
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
 
        # If the two forms are valid...
        if user_form.is_valid():
            if '@' in request.POST['username']:
                user_form = UserForm()
            else:
                # Save the user's form data to the database.
                user = user_form.save()
                
                # Hash the password with the set_password method
                user.set_password(user.password)
                user.is_active = False
                user.save()
                profile = UserProfile(user=user, displayPref = 1)
                profile.save()
                # Update our variable to tell the template registration was successful.
                registered = True
                
                htmlstr =  "<p><a href='https://opra.cs.rpi.edu/auth/register/confirm/"+opra_crypto.encrypt(user.id)+"'>Click This Link To Activate Your Account</a></p>"
                mail.send_mail("OPRA Confirmation","Please confirm your account registration.",'oprahprogramtest@gmail.com',[user.email],html_message=htmlstr)
        #else    print (user_form.errors)
        else:
            return HttpResponse("This user name already exists. Please try a different one. <a href='/auth/register'>Return to registration</a>")
# Not a HTTP POST, so we render our form using two ModelForm instances.
# These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    return render(request,
                              'register.html',
                              {'user_form': user_form, 'registered': registered},
                              context)

							  
def confirm(request, key):
    context = RequestContext(request)
    user_id = opra_crypto.decrypt(key)
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    return render(request, 'activation.html', {}, context)

def quickRegister(request, question_id):
    context = RequestContext(request)
    
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            if '@' in request.POST['username']:
                user_form = UserForm()
            else:
                # Save the user's form data to the database.
                user = user_form.save()
                
                # Hash the password with the set_password method
                user.set_password(user.password)
                user.is_active = False
                user.save()
                profile = UserProfile(user=user, displayPref = 1)
                profile.save()
                # Update our variable to tell the template registration was successful.
                registered = True
                
                htmlstr =  "<p><a href='https://opra.cs.rpi.edu/polls/"+str(question_id)+"/quickconfirm/"+opra_crypto.encrypt(user.id)+"'>Click This Link To Activate Your Account</a></p>"
                mail.send_mail("OPRA Confirmation","Please confirm your account registration.",'oprahprogramtest@gmail.com',[user.email],html_message=htmlstr)
        #else    print (user_form.errors)
        else:
            return HttpResponse("This user name already exists. Please try a different one. <a href='/polls/"+str(question_id)+"'>Return to registration</a>")

def quickConfirm(request,question_id,key):
    user_id = opra_crypto.decrypt(key)
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    login(request,user)
    return HttpResponseRedirect("polls/"+str(question_id)+"/")

def user_login(request):
    context = RequestContext(request)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Check if the username/password combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            return HttpResponse("Your account is not active.")
        else:
            print ("Invalid login details")
            return HttpResponse("Invalid login details supplied.")
	
# Display the login form.
    else:
        return render(request,'login.html', {}, context)


@login_required
def displaySettings(request):
    context = RequestContext(request)
    return render(request,'settings.html', {}, context)

@login_required
def changePasswordView(request):
    context = RequestContext(request)
    return render(request,'changepassword.html', {}, context)

@login_required
def globalSettings(request):
    context = RequestContext(request)
    return render(request,'globalSettings.html', {}, context)

@login_required
def updateSettings(request):
    context = RequestContext(request)
    
    if request.method == 'POST':
        updatedEmail = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        if (first_name == "" and last_name != "") or (first_name != "" and last_name == ""):
            return HttpResponse("Please enter both a first and last name")
	
    try:
        validate_email(updatedEmail)
    except ValidationError as e:
        return HttpResponse("Invalid email")
    else:
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = updatedEmail
        request.user.save()
	
    return HttpResponseRedirect(reverse('appauth:settings'))

@login_required
def updateGlobalSettings(request):
    context = RequestContext(request)
    if request.method == 'POST':
        displayChoice = request.POST['viewpreferences']
        if displayChoice == "always":
            request.user.userprofile.displayPref = 0
        if displayChoice == "allpermit":
            request.user.userprofile.displayPref = 1
        elif displayChoice == "voternames":
            request.user.userprofile.displayPref = 2
        elif displayChoice == "justnumber":
            request.user.userprofile.displayPref = 3
        elif displayChoice == "nothing":
            request.user.userprofile.displayPref = 4
        else:
            request.user.userprofile.displayPref = 5
        request.user.userprofile.emailInvite = request.POST.get('emailInvite') == 'email'
        request.user.userprofile.emailDelete = request.POST.get('emailDelete') == 'email'
        request.user.userprofile.emailStart = request.POST.get('emailStart') == 'email'
        request.user.userprofile.emailStop = request.POST.get('emailStop') == 'email'
        request.user.userprofile.showHint = request.POST.get('showHint') == 'hint'
        request.user.userprofile.save()
        
    return HttpResponseRedirect(reverse('appauth:globalSettings'))

@login_required
def disableHint(request):
    context = RequestContext(request)
    if request.method == 'POST':
        request.user.userprofile.showHint = False
        request.user.userprofile.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # return HttpResponseRedirect(reverse('appauth:logoutCas'))
    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('polls:index_guest'))
    
def forgetPasswordView(request):
    context = RequestContext(request)
    return render(request,'forgetpassword.html', {}, context)
    
class resetPasswordView(generic.DetailView):
    model = User
    template_name = "resetpassword.html"

def forgetPassword(request):
    email = request.POST['email']
    username = request.POST['username']
    if email == "" or username == "":
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    user = get_object_or_404(User, email=email, username=username)
    htmlstr = "<p><a href='" + request.build_absolute_uri("resetpassword/"+str(user.id)) + "'>Click This Link To Reset Password</a></p>"
    print(htmlstr)
    mail.send_mail("OPRA Forget Password","Please click the following link to reset password.",'oprahprogramtest@gmail.com',[email],html_message=htmlstr)
    return HttpResponse("An email has been sent to your email account. Please click on the link in that email and reset your password.")
    
def resetPassword(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    new = request.POST['newpassword']
    con = request.POST['confirmpassword']
    if new != "" and new == con:
        user.set_password(new)
        user.save()
        context = RequestContext(request)
        return render(request,'success.html', {}, context)
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def changepassword(request):
    user = request.user
    old = request.POST['oldpassword']
    new = request.POST['newpassword']
    if user.check_password(old):
        user.set_password(new)
        user.save()
        return HttpResponseRedirect(reverse('polls:index'))
    else:
        return HttpResponse("The password you entered is wrong.")
        
def getRPIUsers():
    users = User.objects.filter(username__contains='@rpi.edu')
    return users
        
class MessageView(generic.ListView):
    template_name = 'messages.html'
    context_object_name = 'message_list'
    def get_queryset(self):
        return Message.objects.all()
    def get_context_data(self, **kwargs):
        ctx = super(MessageView, self).get_context_data(**kwargs)
        permit = []
        permit.append("lirong")
        permit.append("WANGJ33@RPI.EDU")
        permit.append("wangj33@rpi.edu")
        permit.append("xial@rpi.edu")
        permit.append("XIAL@RPI.EDU")
        ctx['rpi_users'] = getRPIUsers()
        ctx['allowed_users'] = permit
        return ctx