import datetime
import time
import random
import uuid
import json
import numpy as np

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
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email

from polls.models import Message, Question, RandomUtilityPool
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
                profile = UserProfile(user=user, displayPref = 1, time_creation=timezone.now())
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
                              {'user_form': user_form, 'registered': registered})

							  
def confirm(request, key):
    context = RequestContext(request)
    user_id = opra_crypto.decrypt(key)
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request,user)
    return render(request, 'activation.html', {'quick':False})

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
                profile = UserProfile(user=user, displayPref = 1,time_creation=timezone.now())
                profile.save()
                # Update our variable to tell the template registration was successful.
                registered = True
                
                htmlstr =  "<p><a href='https://opra.cs.rpi.edu/auth/"+str(question_id)+"/quickconfirm/"+opra_crypto.encrypt(user.id)+"'>Click This Link To Activate Your Account</a></p>"
                mail.send_mail("OPRA Confirmation","Please confirm your account registration.",'oprahprogramtest@gmail.com',[user.email],html_message=htmlstr)
        #else    print (user_form.errors)
        else:
            return HttpResponse("This user name already exists. Please try a different one. <a href='/polls/"+str(question_id)+"'>Return to registration</a>")
    return render(request,
                              'register.html',
                              {'user_form': user_form, 'registered': registered})

def quickConfirm(request,question_id,key):
    user_id = opra_crypto.decrypt(key)
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    context = RequestContext(request)
    link = "/polls/"+ str(question_id)+"/"
    return render(request, 'activation.html', {'quick':True, 'link':link, 'loginkey':key, 'qid':question_id})
    
def quickLogin(request, key, question_id):
    user_id = opra_crypto.decrypt(key)
    user = get_object_or_404(User, pk=user_id)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request,user)
    return HttpResponseRedirect(reverse("polls:detail",args=(question_id,)))
    

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
            else:
                email = user.email
                if email:
                    htmlstr = "Please <a href='https://opra.cs.rpi.edu/auth/register/confirm/"+opra_crypto.encrypt(user.id)+"'>CLICK HERE</a> to activate your account."
                    mail.send_mail("OPRA Confirmation From Invalid Login","Please confirm your account registration.",'oprahprogramtest@gmail.com',[email],html_message=htmlstr)
                return HttpResponse("Your account is not active. We have resent an activation link to your email address. Please check.")
        else:
            return HttpResponse("Invalid login details supplied.")
	
# Display the login form.
    else:
        return render(request,'login.html', {})


@login_required
def displaySettings(request):
    context = RequestContext(request)
    return render(request,'settings.html', {})

@login_required
def changePasswordView(request):
    context = RequestContext(request)
    return render(request,'changepassword.html', {})

@login_required
def globalSettings(request):
    context = RequestContext(request)
    return render(request,'globalSettings.html', {})

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
    return render(request,'forgetpassword.html', {})
    
def resetPage(request, key):
    context = RequestContext(request)
    return render(request,'resetpassword.html',{'key':key})
    

def forgetPassword(request):
    email = request.POST['email']
    username = request.POST['username']
    if email == "" or username == "":
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    user = get_object_or_404(User, email=email, username=username)
    htmlstr = "<p><a href='https://opra.cs.rpi.edu/auth/resetpassword/"+opra_crypto.encrypt(user.id) + "'>Click This Link To Reset Password</a></p>"
    mail.send_mail("OPRA Forget Password","Please click the following link to reset password.",'oprahprogramtest@gmail.com',[email],html_message=htmlstr)
    return HttpResponse("An email has been sent to your email account. Please click on the link in that email and reset your password.")
    
def resetPassword(request, key):
    context = RequestContext(request)
    user_id = opra_crypto.decrypt(key)
    user = get_object_or_404(User, pk=user_id)
    new = request.POST['newpassword']
    con = request.POST['confirmpassword']
    if new != "" and new == con:
        user.set_password(new)
        user.save()
        return render(request,'success.html', {})
    else:
        return render(request,'resetpassword.html',{'key':key})

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

def createMturkUser(request):
    code= uuid.uuid1()
    if request.method == "POST":
        name = request.POST["name"]
        redirect_page = 0
        if name != "" and request.user.username == "":
            age = 0
            try:
                age = int(request.POST["age"])
            except ValueError:
                pass
            newname = name+"@mturk"
            exist = User.objects.filter(username=newname).exists()
            #first_or_last = [42]
            #list1 = [2,3]
            #list2 = [94,97,98,99,100]
            #random.shuffle(list2)
            #flag = random.randrange(2)
            polls = list(range(180,190))
            #random.shuffle(polls)
            # if flag == 1:
                #polls = list1 + first_or_last + list2
                
            #else:
                #polls = list1 + list2 + first_or_last
            polls_str = json.dumps(polls)

            if not exist:
                user = User.objects.create_user(username=newname, password=name)
                profile = UserProfile(user=user,mturk=1,age=age,code=code,sequence=polls_str,cur_poll=polls[0],time_creation=timezone.now(),numq=len(polls))
                profile.save()
                redirect_page = polls[0]
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request,user)
            else:
                user = get_object_or_404(User, username=newname)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request,user)
                if user.userprofile.finished and user.userprofile.cur_poll in polls:
                    return HttpResponseRedirect(reverse('polls:SurveyCode'))
                if user.userprofile.cur_poll in polls and user.userprofile.numq ==len(polls):
                    idx = 0
                    try:
                        user_seq = json.loads(user.userprofile.sequence)
                        idx = user_seq.index(user.userprofile.cur_poll)
                        redirect_page = user.userprofile.cur_poll
                    except ValueError:
                        user.userprofile.sequence = polls_str
                        user.userprofile.cur_poll = polls[0]
                        user.userprofile.numq=len(polls)
                        user.userprofile.save()
                        redirect_page = polls[0]
                else:
                    user.userprofile.sequence = polls_str
                    user.userprofile.cur_poll = polls[0]
                    user.userprofile.numq=len(polls)
                    user.userprofile.save()
                    redirect_page = polls[0]
    
    
                
        elif request.user.username != "":
            #first_or_last = [42]
            #list1 = [2,3]
            #list2 = [94,97,98,99,100]
            #random.shuffle(list2)
            #flag = random.randrange(2)
            polls = list(range(180,190))
            #random.shuffle(polls)
                #if flag == 1:
                #polls = list1 + first_or_last + list2
                #else:
                #polls = list1 + list2 + first_or_last
            polls_str = json.dumps(polls)
            request.user.userprofile.sequence = polls_str
            request.user.userprofile.cur_poll = polls[0]
            request.user.userprofile.numq=len(polls)
            request.user.userprofile.save()
            redirect_page = polls[0]
        #poll_list = list(Question.objects.filter(question_owner = get_object_or_404(User, username="opraexp")))
        return HttpResponseRedirect(reverse('polls:IRBdetail', args=(redirect_page,)))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

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

def resetAllFinish(request):
    if request.user.username == "opraadmin":
        users = User.objects.all()
        for user in users:
            if hasattr(user,'userprofile'):
                if user.userprofile.finished:
                    user.userprofile.finished = False
                    user.userprofile.save()
        #utilitiesList = []
        #alternatives = [10,20,30,40,50,60,70,80,90,100]
        #sigma = 10
        #for i in range(50):
        #    random_utilities = []
        #    for num in alternatives:
        #        base = num
        #        utility = round(np.random.normal(0.0,sigma)+ base)
        #        while utility in random_utilities:
        #            utility = round(np.random.normal(0.0,sigma)+ base)
        #        random_utilities.append((utility,num))
        #    random_utilities.sort()
        #    utilitiesList.append(random_utilities)
        #random_pool = RandomUtilityPool(data=json.dumps(utilitiesList))
        #random_pool.save()

        return HttpResponse("success!")
    else:
        return HttpResponse("failed!")
