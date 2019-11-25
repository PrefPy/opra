from .models import *
from appauth.models import *
from groups.models import *
import datetime
import os
import time
import collections
import dateutil.parser

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.urls import reverse
from django import views
from django.db.models import Q

from django.utils import timezone
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.conf import settings
from django.template import Context

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import *

import json
import threading
import itertools
import numpy as np
import random
import csv
import logging
import random as r
from .match import Matcher
import ast

# Main Page of mentor application
class IndexView(views.generic.ListView):
    template_name = 'mentors/index.html'
    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = self.request.user.userprofile.mentor_applied
        print(ctx['applied'])
        ctx['admin'] = isMentorAdmin(self.request)
        return ctx

    def get_queryset(self):
        return Mentor.objects.all()

def viewindex(request):
    return render(request, 'mentors/index.html', {'applied': request.user.userprofile.mentor_applied, 'admin': isMentorAdmin(request)})

class ApplyView(views.generic.ListView):
    template_name = 'mentors/apply.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyView, self).get_context_data(**kwargs)
        ctx['applied'] = self.request.user.userprofile.mentor_applied

        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

class viewApplictionView(views.generic.ListView):
    template_name = 'mentors/view_application.html'
    def get_context_data(self, **kwargs):
        ctx = super(viewApplictionView, self).get_context_data(**kwargs)
        ctx['user'] = self.request.user.userprofile.mentor_profile
        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

# Admin to view all the applications
class viewStudentsView(views.generic.ListView):
    template_name = 'mentors/view_students.html'
    def get_context_data(self, **kwargs):
        ctx = super(viewStudentsView, self).get_context_data(**kwargs)
        ctx['isAdmin'] = isMentorAdmin(self.request)
        ctx['applicants'] = Mentor.objects.all()
        ctx['applicants_number'] = len(Mentor.objects.all())
        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

# view course features and change their weights
class CourseFeatureView(views.generic.ListView):
    template_name = 'mentors/course_feature.html'
    def get_context_data(self, **kwargs):
        ctx = super(CourseFeatureView, self).get_context_data(**kwargs)
        ctx['courses'] = Course.objects.all()
        return ctx
    def get_queryset(self):
        return Course.objects.all()

class MatchResultView(views.generic.ListView):
    template_name = 'mentors/view_match_result.html'
    def get_context_data(self, **kwargs):
        ctx = super(MatchResultView, self).get_context_data(**kwargs)
        ctx['courses'] = Course.objects.all()
        return ctx
    def get_queryset(self):
        return Course.objects.all()


# apply step
def applystep(request):
    
    this_user = request.user.userprofile
    p = this_user.mentor_profile

    initial={
        'RIN': p.RIN if this_user.mentor_applied else request.session.get('RIN', None), 
        'first_name': p.first_name if this_user.mentor_applied else request.session.get('first_name', None),
        'last_name':  p.last_name if this_user.mentor_applied else request.session.get('last_name', None),
        'GPA':  p.GPA if this_user.mentor_applied else request.session.get('GPA', None),
        'email': request.user.email,
        'phone':  p.phone if this_user.mentor_applied else request.session.get('phone', None),
        'recommender':  p.recommender if this_user.mentor_applied else request.session.get('recommender', None)
    }
    
    print(request.user.userprofile.time_creation)
    form = MentorApplicationfoForm_step1(request.POST or None, initial=initial)
    if request.method == 'POST':
        # initate a new mentor applicant
        if form.is_valid():
            if (this_user.mentor_applied):
                p.RIN = form.cleaned_data['RIN']
                p.first_name = form.cleaned_data['first_name']
                p.last_name = form.cleaned_data['last_name']
                p.GPA = form.cleaned_data['GPA']
                p.email = request.user.email,
                p.phone = form.cleaned_data['phone']
                p.recommender = form.cleaned_data['recommender']
                p.save()
            else:
                request.session['RIN'] = form.cleaned_data['RIN']
                request.session['first_name'] = form.cleaned_data['first_name']
                request.session['last_name'] = form.cleaned_data['last_name']
                request.session['GPA'] = form.cleaned_data['GPA']
                request.session['email'] = request.user.email,
                request.session['phone'] = form.cleaned_data['phone']
                request.session['recommender'] = form.cleaned_data['recommender']
            '''
            pref = new_applicant.course_pref
            pref[new_applicant.RIN] = order_str
            pref.save()

            l = pref[new_applicant.RIN]
            l = [n.strip() for n in ast.literal_eval(l)] # convert str list to actual list u['a', 'b', 'c'] -> ['a', 'b', 'c']
            '''
            return HttpResponseRedirect(reverse('mentors:applystep2'))
            #return render(request, 'mentors/index.html', {'applied': True})
            
        else:
            print(form.errors)
 
    #return HttpResponseRedirect(reverse('groups:members', args=(group.id,)))

    return render(request, 'mentors/apply.html', {'apply_form': form})


# Compensation agreement
def applystep2(request):
    if (checkPage(request, 2)):
        return checkPage(request, 2)
    this_user = request.user.userprofile
    p = this_user.mentor_profile
    initial={
        'compensation': p.compensation if this_user.mentor_applied else request.session.get('compensation', None),
        'studnet_status': p.studnet_status if this_user.mentor_applied else request.session.get('studnet_status', None),
        'employed_paid_before': p.employed_paid_before if this_user.mentor_applied else request.session.get('employed_paid_before', None)
    }
     
    form = MentorApplicationfoForm_step2(request.POST or None, initial=initial)

    if request.method == 'POST':
        if form.is_valid():  
            if (this_user.mentor_applied):
                p.compensation = form.cleaned_data['compensation']
                p.studnet_status = form.cleaned_data['studnet_status']
                p.employed_paid_before = form.cleaned_data['employed_paid_before']   
                p.save()
            else:
                request.session['compensation'] = form.cleaned_data['compensation']
                request.session['studnet_status'] = form.cleaned_data['studnet_status']
                request.session['employed_paid_before'] = form.cleaned_data['employed_paid_before']

            return HttpResponseRedirect(reverse('mentors:applystep3'))
        else:
            print(form.errors)

    return render(request, 'mentors/apply.html', {'apply_form': form})


# Course grade and mentor experience
def applystep3(request):
    if (checkPage(request, 3)):
        return checkPage(request, 3)
    this_user = request.user.userprofile
    p = this_user.mentor_profile

    initial={ 'mentored_non_cs_bf': p.mentored_non_cs_bf if this_user.mentor_applied else request.session.get('mentored_non_cs_bf', None)}
    if (this_user.mentor_applied):
        for course in Course.objects.all():
            this_grade = Grade.objects.filter(course = course, student = p).first()
            course_grade = course.name + "_grade"
            course_exp   = course.name + "_exp"
            initial.update({course_grade:  this_grade.student_grade})
            initial.update({course_exp: 'N' if this_grade.mentor_exp == False else 'Y'})
    else:
        for course in Course.objects.all():
            course_grade = course.name + "_grade"
            course_exp   = course.name + "_exp"
            initial.update({course_grade: request.session.get(course_grade, 'n')})
            initial.update({course_exp: request.session.get(course_exp, 'N')})
    
    
    form = MentorApplicationfoForm_step3(request.POST or None, initial=initial)

    if request.method == 'POST':
        if form.is_valid():   
            if (this_user.mentor_applied):
                p.mentored_non_cs_bf = form.cleaned_data['mentored_non_cs_bf']
                for course in Course.objects.all():
                    course_grade = course.name + "_grade"
                    course_exp   = course.name + "_exp"
                    this_grade = Grade.objects.filter(course = course, student = p).first()
                    this_grade.student_grade = form.cleaned_data[course_grade] # Grade on this course
                    this_grade.mentor_exp = True if form.cleaned_data[course_exp] == 'Y' else False
                    this_grade.save()
                    # if the student has failed the class, or is progressing, we consider he did not take the course
                    if (this_grade.student_grade != 'p' and this_grade.student_grade != 'n' and this_grade.student_grade != 'f'):
                        this_grade.have_taken = True
                    else:
                        this_grade.have_taken = False
                    this_grade.save()
            else:
                request.session['mentored_non_cs_bf'] = form.cleaned_data['mentored_non_cs_bf']
                for course in Course.objects.all():
                    course_grade = course.name + "_grade"
                    course_exp   = course.name + "_exp"
                    request.session[course_grade] = form.cleaned_data[course_grade]
                    request.session[course_exp] = form.cleaned_data[course_exp]
            return HttpResponseRedirect(reverse('mentors:applystep4'))
        else:
            print(form.errors)
    return render(request, 'mentors/apply.html', {'apply_form': form})


# Course preference
def applystep4(request):
    if (checkPage(request, 4)):
        return checkPage(request, 4)
    this_user = request.user.userprofile
    p = this_user.mentor_profile

    initial={ 'pref_order':  p.course_pref if this_user.mentor_applied else request.session.get('pref_order', None),}
    prefer_list = ast.literal_eval(p.course_pref if this_user.mentor_applied else request.session.get('pref_order', '[]'))
         
    course_list = [c.name for c in Course.objects.all()]
    pref_courses = Course.objects.filter(name__in=prefer_list)
    not_pref_courses = Course.objects.filter(name__in=[item for item in course_list if item not in prefer_list])

    #print([i.name for i in pref_courses])
    #print([i.name for i in not_pref_courses])

    #pref_course = Course.objects.filter(name in set(pref_order))
    form = MentorApplicationfoForm_step4(request.POST or None, initial = initial)
    if request.method == 'POST':
        if form.is_valid():    
            
            if (this_user.mentor_applied):
                p.course_pref = form.cleaned_data['pref_order']
                p.save()
            else:
                request.session['pref_order'] = (form.cleaned_data['pref_order'])
            print(request.session['pref_order'])
            #print(breakties(form.cleaned_data['pref_order']))
            return HttpResponseRedirect(reverse('mentors:applystep5'))
        else:
            print(form.errors)
    return render(request, 'mentors/apply.html', {'pref_courses': pref_courses, 'not_pref_courses': not_pref_courses, 'courses':Course.objects.all(), 'apply_form': form})


# Time slots page
def applystep5(request):
    if (checkPage(request, 5)):
        return checkPage(request, 5)
    this_user = request.user.userprofile
    p = this_user.mentor_profile
    initial={
        'time_slots':  p.time_slots if this_user.mentor_applied else request.session.get('time_slots', None),
        'other_times': p.other_times if this_user.mentor_applied else request.session.get('other_times', None),
    }
    
    form = MentorApplicationfoForm_step5(request.POST or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():     
            #order_str = breakties(request.POST['pref_order'])
            if (this_user.mentor_applied):
                p.time_slots = form.cleaned_data['time_slots']
                p.other_times = form.cleaned_data['other_times']
                p.save()
            else:
                request.session['time_slots'] = form.cleaned_data['time_slots']
                request.session['other_times'] = form.cleaned_data['other_times']

            return HttpResponseRedirect(reverse('mentors:applystep6'))
        else:
            print(form.errors)
    return render(request, 'mentors/apply.html', {'courses':Course.objects.all(), 'apply_form': form})


# Students Additional Page
def applystep6(request):
    if (checkPage(request, 6)):
        return checkPage(request, 6)
    this_user = request.user.userprofile
    p = this_user.mentor_profile
    initial={ 'relevant_info': p.relevant_info if this_user.mentor_applied else request.session.get('relevant_info', None),}
     
    form = MentorApplicationfoForm_step6(request.POST or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():     
            if (this_user.mentor_applied):
                p.relevant_info = form.cleaned_data['relevant_info']
                p.save()
            else:
                request.session['relevant_info'] = form.cleaned_data['relevant_info']
                submit_application(request) # Sumbit a new application 
            return HttpResponseRedirect(reverse('mentors:index'))
        else:
            print(form.errors)
    return render(request, 'mentors/apply.html', {'apply_form': form})


# return the prefer after brutally break ties
def breakties(order_str):
    l = []
    order = getPrefOrder(order_str) # change str to double lists
    for i in range(len(order)):
        random.shuffle(order[i]) # break ties with random
        for j in range(len(order[i])):
            l.append(order[i][j])
                
    return l


# Check whether the student finsihed the previous part of the form to prevent the website crash
def checkPage(request, page):
    if (not request.user.userprofile.mentor_applied):
        if (page == 2):
            keys = ['RIN', 'first_name', 'last_name', 'GPA', 'email', 'phone', 'recommender']
        elif (page == 4 or page == 3):
            keys = ['RIN', 'first_name', 'last_name', 'GPA', 'email', 'phone', 'recommender', 'compensation', 'studnet_status', 'employed_paid_before']
        elif (page == 5):
            keys = ['RIN', 'first_name', 'last_name', 'GPA', 'email', 'phone', 'recommender','compensation', 'studnet_status', 'employed_paid_before', 'pref_order']
        elif (page == 6):
            keys = ['RIN', 'first_name', 'last_name', 'GPA', 'email', 'phone', 'recommender','compensation', 'studnet_status', 'employed_paid_before', 'pref_order', 'time_slots', 'other_times']

        for k in keys:
            if (request.session.get(k, None) == None):
                return HttpResponseRedirect(reverse('mentors:index'))
    return False


def submit_application(request):
    new_applicant = Mentor()
    
    new_applicant.RIN = request.session["RIN"]
    new_applicant.first_name = request.session["first_name"]
    new_applicant.last_name = request.session["last_name"]
    new_applicant.GPA = request.session["GPA"]
    new_applicant.phone = request.session["phone"]
    new_applicant.recommender = request.session["recommender"]

    new_applicant.compensation = request.session["compensation"]
    new_applicant.studnet_status = request.session["studnet_status"]
    new_applicant.employed_paid_before = request.session["employed_paid_before"]
    
    new_applicant.mentored_non_cs_bf = request.session["mentored_non_cs_bf"]
    new_applicant.course_pref = request.session["pref_order"]
    new_applicant.time_slots = request.session["time_slots"]
    new_applicant.other_times = request.session["other_times"]
    new_applicant.relevant_info = request.session["relevant_info"]
    new_applicant.save()

    # Save the new application to the profile
    this_user = request.user.userprofile
    this_user.mentor_applied = True
    this_user.mentor_profile = new_applicant
    this_user.save()
    #orderStr = self.cleaned_data["pref_order"]
    
    # Save Grades on the course average
    for course in Course.objects.all():
        course_grade = course.name + "_grade"
        course_exp   = course.name + "_exp"

        new_grade         = Grade()
        new_grade.student = new_applicant
        new_grade.course  = course
        new_grade.student_grade = request.session[course_grade] # Grade on this course
        new_grade.save()

        if (request.session[course_exp] == 'Y'): # Mentor Experience
            new_grade.mentor_exp = True
        else:
            new_grade.mentor_exp = False

        # if the student has failed the class, or is progressing, we consider he did not take the course
        if (new_grade.student_grade != 'p' and new_grade.student_grade != 'n' and new_grade.student_grade != 'f'):
            new_grade.have_taken = True
        else:
            new_grade.have_taken = False
        new_grade.save()
        print(new_grade.course.name + ": " + new_grade.student_grade)
    return new_applicant


# withdraw application, should add semester later
def withdraw(request):
    if request.method == 'GET':
        try:
            #request.user.userprofile.mentor_profile.delete()
            request.user.userprofile.mentor_applied = False
            request.user.userprofile.save()
            request.user.save()
        except:
            print('Can not delete mentor application')
        # Clear sessions
        # request.session.flush()
    HttpResponseRedirect(reverse('mentors:index'))
    
# load CS_Course.csv to generate courses
def addcourse(request):
    #Course.objects.all().delete()
    #print(new_course.class_title + new_course.class_number + new_course.class_name + "successfully added")
    if request.method == 'POST' and request.FILES['myfile']:
        file = request.FILES['myfile']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)

        for row in reader:
        
            c, created = Course.objects.get_or_create(
                name = row[0],
                subject = row[1],
                number = row[2],
            )
            c.time_slots = row[4] if row[4].strip()!="" else "[]"
            c.mentor_cap = row[3]
            c.feature_cumlative_GPA = 1
            c.feature_has_taken = 1
            c.feature_course_GPA = 1
            c.feature_mentor_exp = 1
            c.save()
            print(row[0] + " " + row[1] + " " + row[2] +" "+ row[3] + " successfully added/changed.")

    return HttpResponseRedirect(reverse('mentors:index'))

# Return the course searched
def searchCourse(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        course_name = request.POST.get('courses', False)
        choosen_course = Course.objects.filter(name = course_name).first()
        time_slots = Context()
        time_slots["times"] = []
        for t in ast.literal_eval(choosen_course.time_slots):
            time_slots["times"].append(t)
    return render(request, 'mentors/course_feature.html', {'courses': courses, 'choosen_course': choosen_course, 'time_slots': time_slots})


# Change the value of features of a selected course
def changeFeature(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        
        course_name = request.POST.get('course', False)

        choosen_course = Course.objects.filter(name = course_name).first()
        choosen_course.feature_cumlative_GPA = request.POST.get('f1', False)
        choosen_course.feature_course_GPA= request.POST.get('f2', False)
        choosen_course.feature_has_taken = request.POST.get('f3', False)
        choosen_course.feature_mentor_exp = request.POST.get('f4', False)
        choosen_course.save()
    return render(request, 'mentors/course_feature.html', {'courses': courses, 'choosen_course': choosen_course})



# Randomly add students with assigned numbers
def addStudentRandom(request):
    classes = [course.name for course in Course.objects.all()]
    numClass = len(Course.objects.all())

    if request.method == 'POST':
        Mentor.objects.all().delete()
        num_students = request.POST['num_students']
        for i in range(int(num_students)):
            new_applicant = Mentor()
            new_applicant.RIN = str(100000000 + i)
            new_applicant.first_name = "student_"
            new_applicant.last_name = str(i)
            new_applicant.GPA = round(random.uniform(2.0, 4)*100)/100 # simple round
            new_applicant.phone = 518596666
            '''
            pref = Dict()
            pref.name = new_applicant.RIN
            pref.save()
            new_applicant.course_pref = pref
            new_applicant.save()
            new_applicant.course_pref[new_applicant.RIN] = r.sample(classes, r.randint(1, numClass))
            '''
            new_applicant.course_pref = r.sample(classes, r.randint(1, numClass))
            print(new_applicant.course_pref)
            new_applicant.save()

            for course in Course.objects.all():
                new_grade = Grade(id=None)
                #glist  = ['a','a-','b+','b','b-','c+','c','c-','d+','d','f','p','n']
                glist = ['a','a-','b+','b','b-','c','c+','n']

                new_grade.student_grade = random.choice(glist)
                if (new_grade.student_grade != 'p' and new_grade.student_grade != 'n' and new_grade.student_grade != 'f'):
                    new_grade.have_taken = True
                    new_grade.mentor_exp = random.choice([True, False])
                else:
                    new_grade.have_taken = False
                    new_grade.mentor_exp = False

                new_grade.course = course
                new_grade.student = new_applicant
                new_grade.save()

            #print("Add a new student: " + new_applicant.first_name + new_applicant.last_name + ": GPA: " + str(new_applicant.GPA))
        print("students now: " + str(len(Mentor.objects.all())))
    return HttpResponseRedirect(reverse('mentors:index'))


def StartMatch(request):
    if request.method == 'POST':
        grade_weights = {   'a':    4,    'a-':   3.69,
                            'b+':   3.33, 'b':    3, 'b-':   2.67,
                            'c+':   2.33, 'c':    2, 'c-':   1.67,
                            'd+':   1.33, 'd':    1, 'f':    0,
                            'p':    0,    'n':    0, 'ap':   4,}

        # begin matching:
        studentFeatures = {}
        for s in Mentor.objects.all():
            studentFeatures_per_course = {}
            #print(s)
            for c in Course.objects.all():
                item = Grade.objects.filter(student = s, course = c).first()
                studentFeatures_per_course.update(
                    {c.name:(
                            s.GPA/4*100,
                            grade_weights.get(item.student_grade)/4*100,
                            int(item.have_taken)*100,
                            int(item.mentor_exp)*100
                            )
                    }
                )
            #print([i.student_grade for i in s.grade_set.all()])
            studentFeatures.update({s.RIN: studentFeatures_per_course})


        numFeatures = 4 # number of features we got
        classes = [c.name for c in Course.objects.all()]
        classCaps = {c.name: c.mentor_cap for c in Course.objects.all()}
        students = [s.RIN for s in Mentor.objects.all()]
        studentPrefs = {s.RIN: ast.literal_eval(s.course_pref) for s in Mentor.objects.all()}
        classFeatures = {c.name: (c.feature_cumlative_GPA, c.feature_course_GPA, c.feature_has_taken, c.feature_mentor_exp) for c in Course.objects.all()}
        matcher = Matcher(studentPrefs, studentFeatures, classCaps, classFeatures)
        classMatching = matcher.match()

        assert matcher.isStable()
        print("matching is stable\n")
        
        #print out some classes and students
        for (course, student_list) in classMatching.items():
            print(course + ", cap: " + str(classCaps[course]) + ", features: ", classFeatures[course])
            this_course  = Course.objects.filter(name = course).first()

            for s_rin in student_list:        
                this_student = Mentor.objects.filter(RIN = s_rin).first()
                item = Grade.objects.filter(student = this_student, course = this_course).first()

                print("   " + s_rin + " cumlative GPA: " + str(this_student.GPA).upper() + " grade: " + item.student_grade.upper() + ", has mentor exp: " + str(item.mentor_exp) )

                #assign the course to this student
                this_student.mentored_course = this_course
                this_student.save()
       
        unmatchedClasses = set(classes) - classMatching.keys()
        unmatchedStudents = set(students) - matcher.studentMatching.keys()
        print(f"{len(unmatchedClasses)} classes with no students")
        print(f"{len(unmatchedStudents)} students not in a class")


    return render(request, 'mentors/view_match_result.html', {'result': viewMatchResult()})

def viewResultPage(request):
    return render(request, 'mentors/view_match_result.html', {'result': viewMatchResult()})

def viewMatchResult():
    # create a context to store the results
    result = Context()
    result["courses"] = [] # list of courses
    for course in Course.objects.all():
        mentor_list = []
        for student in course.mentor_set.all():
            item = Grade.objects.filter(student = student, course = course).first()
            new_mentor = {"name": student.first_name+" "+student.last_name, "GPA": student.GPA, "grade": item.student_grade.upper(), "Exp": str(item.mentor_exp)}
            mentor_list.append(new_mentor)

        result["courses"].append({"name": str(course),
                                    "number": str(course.number),
                                    "features": (course.feature_cumlative_GPA, course.feature_course_GPA, course.feature_has_taken, course.feature_mentor_exp) , 
                                    "mentors": mentor_list})
    return result


def isMentorAdmin(request):
    Admin_Email_List = ["cheny42@rpi.edu", "xial@rpi.edu", "hulbes@rpi.edu", "goldsd3@rpi.edu" ]
    if (request.user.email.strip() in Admin_Email_List):
        return True
    print(request.user.email.strip())
    return False

# csv download fucntion
def download_mentor_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="S20-UG-mentor-applicants.csv"'

    writer = csv.writer(response)
    row = ['RIN', 'Last Name', 'First Name', 'Email', 'Phone', 'GPA', 'Recommender', 'Compensation', 'Paid Before?', 'Status', 'Info', 'Mentored_nonCS']
    for course in Course.objects.all():
        course_prefix = course.subject + '_' + course.number
        g = course_prefix+'_Grade'
        m = course_prefix+'_Mentored'
        row.append(g)
        row.append(m)
        
    for course in Course.objects.all():
        for t in ast.literal_eval(course.time_slots):
            ct = course.subject + '_' + course.number + '_' + t
            row.append(ct)
    row.append("Other Times")
    writer.writerow(row)
    comp = {
        "n": "Either",
        "p": "Pay",
        "c": 'Credit'
    }
    status = {
        "i": "International",
        "d": "Domestic",
    }
    for m in Mentor.objects.all():
        row = [m.RIN, m.first_name, m.last_name, str(m.email), m.phone, m.GPA, m.recommender, comp[m.compensation], "paidbyrpi" if m.employed_paid_before else "", status[m.studnet_status], m.relevant_info.replace('"', '\'').replace('/[\n\r]+/', ' '), m.mentored_non_cs_bf]
        for course in Course.objects.all():
            grade = Grade.objects.filter(course = course, student = m).first()
            course_prefix = course.subject + " " + course.number
            row.append(grade.student_grade.upper())
            row.append("Yes" if grade.mentor_exp else "")
        for course in Course.objects.all():
            for course_time in ast.literal_eval(course.time_slots):
                if(course_time in [i.replace('_', ' ') for i in ast.literal_eval( m.time_slots)]):
                    if (course.name in ast.literal_eval(m.course_pref)):
                        row.append("wantstomentor")
                    else:
                        row.append("")
                else:
                    row.append("")
        row.append(m.other_times.replace('/[\n\r]+/', '').replace('"', '\''))
        writer.writerow(row)
    
    return response


# function to get preference order from a string
# String orderStr
# Question question
# return List<List<String>> prefOrder
def getPrefOrder(orderStr):
    # empty string
    if orderStr == "":
        return None
    if ";;|;;" in orderStr:
        current_array = orderStr.split(";;|;;")
        final_order = []
        length = 0
        for item in current_array:
            if item != "":
                curr = item.split(";;")
                final_order.append(curr)
                length += len(curr)
    else:
        final_order = json.loads(orderStr)
    
    
    return final_order


