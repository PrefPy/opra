from .models import *
from appauth.models import *
from groups.models import *
import datetime
import os
import time
import collections

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

class IndexView(views.generic.ListView):
    """
        Define homepage view, inheriting ListView class, which specifies a context variable.

        Note that login is required to view the items on the page.
        """

    template_name = 'mentors/index.html'
    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)

        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        return ctx

    def get_queryset(self):
        """Override function in parent class and return all questions."""

        return Mentor.objects.all()

class ApplyView(views.generic.ListView):
    template_name = 'mentors/apply.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()
        ctx['step'] = Mentor.step

        if (Mentor.applied):
            ctx['step'] = Mentor.step
        else:
            ctx['step'] = 1
            Mentor.step = 1

        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

class view_applyView(views.generic.ListView):
    template_name = 'mentors/view_application.html'
    def get_context_data(self, **kwargs):
        ctx = super(view_applyView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()

        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

# view of personal infomation page
class ApplyPersonalInfoView(views.generic.ListView):
    template_name = 'mentors/apply_personal_info.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyPersonalInfoView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()

        return ctx
    def get_queryset(self):
        return Mentor.objects.all()

# view of compensation and reponsibility page
class ApplyCompensationView(views.generic.ListView):
    template_name = 'mentors/apply_compensation.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyCompensationView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()
        ctx['step'] = Mentor.step

        return ctx

    def get_queryset(self):
        return Mentor.objects.all()

# view of preference of a student applicant page
class ApplyPreferenceView(views.generic.ListView):
    template_name = 'mentors/apply_preference.html'
    def get_context_data(self, **kwargs):
        ctx = super(ApplyPreferenceView, self).get_context_data(**kwargs)
        # check if there exist a mentor application
        ctx['applied'] = Mentor.applied
        ctx['applications'] = Mentor.objects.all()
        ctx['step'] = Mentor.step
        # === need more for course data ===
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
    if request.method == 'POST':
        # initate a new mentor applicant
        form = MentorApplicationfoForm(request.POST)
        if form.is_valid():
            new_applicant = form.save()
            order_str = breakties(request.POST['pref_order'])

            pref = new_applicant.course_pref
            pref[new_applicant.RIN] = order_str
            pref.save()

            l = pref[new_applicant.RIN]
            l = [n.strip() for n in ast.literal_eval(l)] # convert str list to actual list u['a', 'b', 'c'] -> ['a', 'b', 'c']

            return render(request, 'mentors/index.html', {'applied': True})
        else:
            print(form.errors)

    else:  # display empty form
        form = MentorApplicationfoForm()

        #Mentor.applied = True
   
    #return HttpResponseRedirect(reverse('groups:members', args=(group.id,)))
    courses = Course.objects.all()

    return render(request, 'mentors/apply.html', {'courses': courses, 'apply_form': form})


# return the prefer after brutally break ties
def breakties(order_str):
    l = []
    order = getPrefOrder(order_str) # change str to double lists
    for i in range(len(order)):
        random.shuffle(order[i]) # break ties with random
        for j in range(len(order[i])):
            l.append(order[i][j])
                
    return l

# withdraw application, should add semester later
def withdraw(request):
    if request.method == 'GET':
        Mentor.objects.all().delete()
        Mentor.applied = False
    return HttpResponseRedirect(reverse('mentors:index'))

# load CS_Course.csv 
def addcourse(request):
    if request.method == 'POST':
        Course.objects.all().delete()
        #print(new_course.class_title + new_course.class_number + new_course.class_name + "successfully added")
        with open("mentors/CS_Course.csv") as f:
            reader = csv.reader(f)
            for row in reader:
                _ = Course.objects.get_or_create(
                    name = row[0],
                    subject = row[1],
                    number = row[2],
                    instructor = row[3],
                    mentor_cap = r.randint(3, 10),
                    feature_cumlative_GPA = r.randint(3, 10),
                    feature_has_taken = r.randint(0, 10),
                    feature_course_GPA = r.randint(3, 10),
                    feature_mentor_exp = r.randint(0, 10),
                )
                print(row[0] + " " + row[1] + " " + row[2] + " successfully added.")

    return render(request, 'mentors/index.html', {})

def searchCourse(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        
        course_name = request.POST.get('courses', False)
        choosen_course = Course.objects.filter(name = course_name).first()
    return render(request, 'mentors/course_feature.html', {'courses': courses, 'choosen_course': choosen_course})

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
        #Mentor.objects.all().delete()

        num_students = request.POST['num_students']
        for i in range(int(num_students)):
            new_applicant = Mentor()
            new_applicant.RIN = str(100000000 + i)
            new_applicant.first_name = "student_"
            new_applicant.last_name = str(i)
            new_applicant.GPA = round(random.uniform(2.0, 4)*100)/100 # simple round
            new_applicant.phone = 518596666

            pref = Dict()
            pref.name = new_applicant.RIN
            pref.save()
            new_applicant.course_pref = pref
            new_applicant.save()

            new_applicant.course_pref[new_applicant.RIN] = r.sample(classes, r.randint(1, numClass))
            for course in Course.objects.all():
                new_grade = Grade(id=None)
                #glist  = ['a','a-','b+','b','b-','c+','c','c-','d+','d','f','p','n']
                glist  = ['a','a-','b+','b','b-','c','c+','n']

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
    return render(request, 'mentors/index.html', {})


def StartMatch(request):
    if request.method == 'POST':
        grade_weights = {   'a':    4,    'a-':   3.69,
                            'b+':   3.33, 'b':    3, 'b-':   2.67,
                            'c+':   2.33, 'c':    2, 'c-':   1.67,
                            'd+':   1.33, 'd':    1, 'f':    0,
                            'p':    0,    'n':    0}

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
        numClasses = len(Course.objects.all())
        studentPrefs = {s.RIN: [n.strip() for n in ast.literal_eval(s.course_pref[s.RIN])] for s in Mentor.objects.all()}


        #studentPrefs = {s: [c for c in r.sample(classes, r.randint(numClasses, numClasses ))] for s in students}
        #studentFeatures = {s: {c: tuple(r.randint(0, 10) for i in range(numFeatures)) for c in classRank} for s, classRank in studentPrefs.items()}
        classFeatures = {c.name: (c.feature_cumlative_GPA, c.feature_course_GPA, c.feature_has_taken, c.feature_mentor_exp) for c in Course.objects.all()}
        #classFeatures = {c: (0, 1000, 5, 5) for c in classes}

        matcher = Matcher(studentPrefs, studentFeatures, classCaps, classFeatures)
        classMatching = matcher.match()

        
        assert matcher.isStable()
        print("matching is stable\n")
        

        # create a context to store the results
        result = Context()
        result["courses"] = [] # list of courses

        #print out some classes and students
        for (course, student_list) in classMatching.items():
            print(course + ", cap: " + str(classCaps[course]) + ", features: ", classFeatures[course])
            this_course  = Course.objects.filter(name = course).first()

            mentor_list = []
            for s_rin in student_list:        
                this_student = Mentor.objects.filter(RIN = s_rin).first()
                item = Grade.objects.filter(student = this_student, course = this_course).first()

                print("   " + s_rin + " cumlative GPA: " + str(this_student.GPA).upper() + " grade: " + item.student_grade.upper() + ", has mentor exp: " + str(item.mentor_exp) )

                #assign the course to this student
                this_student.mentored_course = this_course
                this_student.save()

                new_mentor = {"name": this_student.first_name+" "+this_student.last_name, "GPA": this_student.GPA, "grade": item.student_grade.upper(), "Exp": str(item.mentor_exp)}
                mentor_list.append(new_mentor)
            
            print()
            result["courses"].append({"name": str(this_course), "mentors": mentor_list})
       
        unmatchedClasses = set(classes) - classMatching.keys()
        unmatchedStudents = set(students) - matcher.studentMatching.keys()
        print(f"{len(unmatchedClasses)} classes with no students")
        print(f"{len(unmatchedStudents)} students not in a class")

    
    return render(request, 'mentors/view_match_result.html', {'result': result})

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

