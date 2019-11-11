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
from prefpy.mechanism import *
from prefpy.allocation_mechanism import *
from prefpy.gmm_mixpl import *
from prefpy.egmm_mixpl import *
from django.conf import settings
from multipolls.models import *

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

# apply step
def applystep(request):
    if request.method == 'POST':
        # initate a new mentor applicant
        form = MentorApplicationfoForm(request.POST)
        if form.is_valid():
            form.save()
            print("yes")
        else:
            print(form.errors)

    else:  # display empty form
        print("empty")
        form = MentorApplicationfoForm()

        #Mentor.applied = True
        #Mentor.step += 1
    #return HttpResponseRedirect(reverse('groups:members', args=(group.id,)))
    courses = Course.objects.all()

    return render(request, 'mentors/apply.html', {'courses': courses, 'apply_form': form})


# withdraw application, should add semester later
def withdraw(request):
    if request.method == 'GET':
        Mentor.objects.all().delete()
        Mentor.applied = False
    return HttpResponseRedirect(reverse('mentors:index'))


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
                    )
                print(row[0] + " " + row[1] + " " + row[2] + " successfully added.")

    return render(request, 'mentors/index.html', {})

# Randomly add students
def addStudentRandom(request):
    if request.method == 'POST':
        Mentor.objects.all().delete()

        num_students = request.POST['num_students']
        for i in range(int(num_students)):
            new_applicant = Mentor()
            new_applicant.RIN = str(661680900 + i)
            new_applicant.first_name = "student_"
            new_applicant.last_name = str(i)
            new_applicant.GPA = round(random.uniform(2.5, 4)*100)/100 # simple round
            new_applicant.phone = 518596666
            new_applicant.save()

            for course in Course.objects.all():
                new_grade = Grade(id=None)
                #glist  = ['a','a-','b+','b','b-','c+','c','c-','d+','d','f','p','n']
                #new_grade.id = None
                glist  = ['a','a-','b+','b','b-','c','c+''n']

                new_grade.student_grade = random.choice(glist)
                if (new_grade.student_grade != 'p' and new_grade.student_grade != 'n' and new_grade.student_grade != 'f'):
                    new_grade.have_taken = True
                    new_grade.mentor_exp = random.choice([True, False])
                else:
                    new_grade.have_taken = False
                    new_grade.mentor_exp = False

                #new_grade.have_taken = random.choice([True, False])
                #new_grade.mentor_exp = random.choice([True, False])
                new_grade.course = course
                new_grade.student = new_applicant
                new_grade.save()

            #print("Add a new student: " + new_applicant.first_name + new_applicant.last_name + ": GPA: " + str(new_applicant.GPA))
        print("students now: " + str(len(Mentor.objects.all())))
    return render(request, 'mentors/index.html', {})


def StartMatch(request):
    if request.method == 'POST':
        grade_weights = {   'a':    4,
                            'a-':   3.69,
                            'b+':   3.33,
                            'b':    3,
                            'b-':   2.67,
                            'c+':   2.33,
                            'c':    2,
                            'c-':   1.67,
                            'd+':   1.33,
                            'd':    1,
                            'f':    0,
                            'p':    0,
                            'n':    0}

        # begin matching:
        studentFeatures = {}
        for s in Mentor.objects.all():
            studentFeatures_per_course = {}
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

            studentFeatures.update({s.RIN: studentFeatures_per_course})


        numFeatures = 4 # number of features we got
        classes = [course.name for course in Course.objects.all()]
        classCaps = {c: r.randint(3, 10) for c in classes}
        students = [studnet.RIN for studnet in Mentor.objects.all()]
        numClasses = len(Course.objects.all())

        studentPrefs = {s: [c for c in r.sample(classes, r.randint(numClasses, numClasses ))] for s in students}
        #print(studentPrefs)
        #studentFeatures = {s: {c: tuple(r.randint(0, 10) for i in range(numFeatures)) for c in classRank} for s, classRank in studentPrefs.items()}
        #print(studentFeatures)
        classFeatures = {c: (r.randint(3, 10), r.randint(3, 10), r.randint(1, 10), r.randint(1, 10)) for c in classes}
       # classFeatures = {c: (0, 1000, 5, 5) for c in classes}

        matcher = Matcher(studentPrefs, studentFeatures, classCaps, classFeatures)
        classMatching = matcher.match()
        '''
        assert matcher.isStable()
        print("matching is stable\n")
        '''
        #print out some classes and students
        for (course, student_list) in classMatching.items():
            print(course)
            for s in student_list:
                
                this_student = Mentor.objects.filter(RIN = s).first()
                this_course  = Course.objects.filter(name = course).first()
                query = Grade.objects.filter(student = this_student, course = this_course)
                item = query.first()
                print("   "+s + " cumlative GPA: " + str(this_student.GPA).upper() + " grade: " + item.student_grade.upper() + ", has mentor exp: " + str(item.mentor_exp) )

                #print("   ",s , studentFeatures[s][course])

            print()

        unmatchedClasses = set(classes) - classMatching.keys()
        unmatchedStudents = set(students) - matcher.studentMatching.keys()

        #unmatchedStudents uses the non-returned output matcher.studentMatching
        #it's a dict from student to class they're in

        print(f"{len(unmatchedClasses)} classes with no students")
        print(f"{len(unmatchedStudents)} students not in a class")
    return render(request, 'mentors/index.html', {})
