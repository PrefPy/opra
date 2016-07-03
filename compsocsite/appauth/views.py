import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic

from .models import *

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
            # Save the user's form data to the database.
            user = user_form.save()
            
            # Hash the password with the set_password method
            user.set_password(user.password)
            user.save()
            profile = UserProfile(user=user, displayPref = 1)
            profile.save()
            # Update our variable to tell the template registration was successful.
            registered = True

        #else    print (user_form.errors)

# Not a HTTP POST, so we render our form using two ModelForm instances.
# These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    return render_to_response(
                              'register.html',
                              {'user_form': user_form, 'registered': registered},
                              context)

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
                return HttpResponseRedirect('/polls/')
            return HttpResponse("Your account is disabled.")
        else:
            print ("Invalid login details")
            return HttpResponse("Invalid login details supplied.")
	
# Display the login form.
    else:
        return render_to_response('login.html', {}, context)


@login_required
def displaySettings(request):
    context = RequestContext(request)
    return render_to_response('settings.html', {}, context)

@login_required
def changePasswordView(request):
    context = RequestContext(request)
    return render_to_response('changepassword.html', {}, context)

@login_required
def globalSettings(request):
    context = RequestContext(request)
    return render_to_response('globalSettings.html', {}, context)

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
    if request.method == 'POST':
        displayChoice = request.POST['viewpreferences']
        if displayChoice == "allpermit":
            request.user.userprofile.displayPref = 1
        elif displayChoice == "voternames":
            request.user.userprofile.displayPref = 2
        elif displayChoice == "justnumber":
            request.user.userprofile.displayPref = 3
        else:
            request.user.userprofile.displayPref = 4
        request.user.userprofile.emailInvite = request.POST.get('emailInvite') == 'email'
        request.user.userprofile.emailDelete = request.POST.get('emailDelete') == 'email'
        request.user.userprofile.emailStart = request.POST.get('emailStart') == 'email'
        request.user.userprofile.emailStop = request.POST.get('emailStop') == 'email'
        request.user.userprofile.save()
	
    return HttpResponseRedirect('/auth/settings/')    

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    
    # Take the user back to the homepage.
    return HttpResponseRedirect('/polls/')
    
@login_required
def changepassword(request):
    user = request.user
    old = request.POST['oldpassword']
    new = request.POST['newpassword']
    if user.check_password(old):
        user.set_password(new)
        user.save()
        return HttpResponseRedirect('/polls/')
    else:
        return HttpResponse("The password you entered is wrong.")