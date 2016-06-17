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
    
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
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
            
            # Update our variable to tell the template registration was successful.
            registered = True
        
        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        #else    print (user_form.errors)

# Not a HTTP POST, so we render our form using two ModelForm instances.
# These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    # Render the template depending on the context.
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
def updateSettings(request):
    context = RequestContext(request)
    
    if request.method == 'POST':
        updatedEmail = request.POST['email']
	
    try:
	validate_email(updatedEmail)
    except ValidationError as e:
        return HttpResponse("Invalid email")
    else:
	request.user.email = updatedEmail
	request.user.save()
	
    return HttpResponseRedirect('/auth/settings/')    

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    
    # Take the user back to the homepage.
    return HttpResponseRedirect('/polls/')
