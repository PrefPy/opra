from django import forms
from .models import *
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

# import crispy form plugin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

class MentorApplicationfoForm_step1(ModelForm):
    class Meta:
        model = Mentor
        #fields = '__all__' 
        fields = (  'RIN', 
                    'first_name', 
                    'last_name',
                    'GPA',
                    'email',
                    'phone',
                    'recommender',
                )
        widgets = {
            'RIN': forms.TextInput(attrs={'placeholder': ' 661680100'}),
            'GPA': forms.TextInput(attrs={'placeholder': ' 3.6'}),
            'email': forms.TextInput(attrs={'readonly':'readonly', "style": "color:blue;"}), # Read-only email
            'phone': forms.TextInput(attrs={'placeholder': ' 5185941234'}),
        }
    def __init__(self, *args, **kwargs):
        super(MentorApplicationfoForm_step1, self).__init__(*args, **kwargs)  
        self.helper = FormHelper()
        self.fields['recommender'].required = False
        self.helper.layout = Layout(
            HTML('== PERSONAL INFORMATION =='),
            HTML("<fieldset>"),
            Div('RIN', css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),
            Div('first_name', css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),
            Div('last_name', css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),

            Div('email',css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),

            Div('phone', css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),

            Div('GPA', css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),
            HTML(""" <div class = 'vspacewithline'> </div>"""),
            HTML("""
            <div class = 'textline'>Please provide the name of someone in the CS Department who can recommend you. You are encouraged, but not required, to contact this person.
             Please provide only a name here (describe additional circumstances in the freeform textbox below).</div>
            """),
            Div('recommender', css_class = "inputline"),
            HTML("</fieldset>"),
        )
        self.helper.form_method = 'POST'
        self.helper.label_class = "inputline"
        self.helper.add_input(Submit('next', 'Next'))

class MentorApplicationfoForm_step2(ModelForm):
    class Meta:
        model = Mentor
        #fields = '__all__' 
        fields = ( 'compensation', 'studnet_status', 'employed_paid_before')
    def __init__(self, *args, **kwargs):
        super(MentorApplicationfoForm_step2, self).__init__(*args, **kwargs)  
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('''<p class = 'form_title'> COMPENSATION AND RESPONSIBILITIES </p>  '''),
            HTML(""" <div class = 'emptyspace'> </div>"""),

            HTML("<fieldset>"),
            HTML("""
            <div class = "textline">
                We currently have funding for a fixed number of paid programming mentors. Therefore, if you apply for pay, you may be asked to work for credit instead. Course credit counts as a graded 1-credit or 2-credit free elective. In general, if you work an average of 1-3 hours per week, you will receive 1 credit; if you average 4 or more hours per week, you will receive 2 credits. Note that no more than 4 credits may be earned as an undergraduate (spanning all courses and all semesters). Please do not apply for credit if you have already earned 4 credits as a mentor; apply only for pay.
            </div>
            """),
            HTML(""" <div class = 'vspacewithline'> </div>"""),

            HTML("""<label class = 'inputline' style = "float: left;"> Select your compensations: </label>"""),
            Div('compensation', css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),

            HTML("""<label class = 'inputline' style = "float: left;"> I have been employed and paid by RPI before: </label>"""),
            Div('employed_paid_before', css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),

            HTML("""<label class = 'inputline' style = "float: left;"> Please specify your student status: </label>"""),
            Div('studnet_status', css_class = "inputline"),
            HTML(""" <div class = 'emptyspace'> </div>"""),

            HTML(""" <div class = 'vspacewithline'> </div>"""),
            HTML(""" <div class="textline">For a paid position, you <strong>must</strong> follow the given instructions to ensure you are paid; otherwise, 
            another candidate will be selected.  More specifically, you will be required to have a <strong>student employment card</strong>.  This requires 
            you to have a federal I-9 on file.  Bring appropriate identification with you to Amos Eaton&nbsp;125 if this is your first time working for RPI; 
            <strong><a style = "color:red;" href="https://www.uscis.gov/i-9-central/acceptable-documents" target="_blank">click here for a list of acceptable documents.</a></strong>  
            <strong>Note that original documents are required; copies cannot be accepted.</strong> </div>"""),

            HTML(""" <div class="textline"><strong>Detailed instructions are listed here: <a style = "color:red;" href="https://info.rpi.edu/student-employment/required-documents" 
            target="_blank">https://info.rpi.edu/student-employment/required-documents</a></strong></div>"""),

            HTML(""" <div class="textline">Please note that to be paid, you will be required to submit your specific hours in SIS 
            every two weeks.  This <strong>must</strong> be completed to get paid on time, and any late submissions will incur a fee charged to the department.</div>"""),

            HTML(""" <div class="textline">If you are unable to attend your assigned labs or office hours (e.g., illness, interview, conference, etc.), you <strong>must</strong> 
            notify your graduate lab TA and instructor and help arrange a substitute mentor.  Unexcused absences will cause you to either earn a lower letter grade or not be asked to mentor again.</div>"""),
            HTML("</fieldset>"),

        )
        self.helper.form_method = 'POST'
        self.helper.label_class = "my_label"
        self.helper.form_show_labels = False
        self.helper.add_input(Button('prev', 'Prev', onclick="window.history.go(-1); return false;"))
        self.helper.add_input(Submit('next', 'Next'))

class MentorApplicationfoForm_step3(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MentorApplicationfoForm_step3, self).__init__(*args, **kwargs)  
        self.helper = FormHelper()
        courses = Course.objects.all()
        course_layout = Field()
        for course in courses:     
            course_layout.append(HTML(''' <div class ="col-md-4">'''))
            course_layout.append(HTML('''<div class = 'course_title' style="float:left;">''' + str(course.name)+ "</div>") )
            course_layout.append(HTML('''<div style="width: 330px; min-height: 80px; float:left;">''' + str(course.subject+" "+course.number)+ "</div>") )

            course_layout.append(HTML("&nbsp; &nbsp; &nbsp;"))
            course_layout.append(HTML(''' </div>'''))
            grades = (
                     ('a', 'A'), ('a-', 'A-'),
                     ('b+', 'B+'), ('b', 'B'), ('b-', 'B-'),
                     ('c+', 'C+'), ('c', 'C'), ('c-', 'C-'),
                     ('d+', 'D+'), ('d', 'D'), ('f', 'F'),
                     ('p', 'Progressing'), ('n', 'Not Taken'),
                     )
            choices_YN = (
                    ('Y', 'YES'),
                    ('N', 'NO'),
            )
            self.fields[course.name+ "_grade"] = forms.ChoiceField(
                choices = grades, 
                label = "Grade on this course:",
            ) 
            #self.initial[course.name+ "_grade"] = 'n'
            self.fields[course.name+ "_exp"] = forms.ChoiceField(choices = choices_YN, label = "")
            #self.initial[course.name+ "_exp"] = 'N'
            course_layout.append(HTML(''' <div class ="col-md-8">'''))

            course_layout.append(HTML("""<p style = "float: left;" > I have taken this course at RPI before and earned grade: &nbsp </p>"""))
            course_layout.append(Field(course.name+ "_grade", label_class="float: left;"))
            course_layout.append(HTML(""" <div class = 'emptyspace'> </div>"""))
            course_layout.append(HTML("""<p style = "float: left;"> I have mentored this RPI course before: &nbsp </p>"""))
            course_layout.append(Field(course.name+ "_exp"))
            course_layout.append(HTML(''' </div>'''))

            course_layout.append(HTML(""" <div class = 'vspacewithline'> </div>""")),


        self.helper.layout = Layout(
            HTML('== COURSE EXPERIENCE =='),
            HTML("<fieldset>"),
            HTML('''<div class = 'textline'> Below is a list of courses likely to need mentors. Note that CSCI 1100 is in
             Python, CSCI 1190 is in MATLAB, CSCI 1200 is in C++, CSCI 2300 is in Python/C++, CSCI 2500 
             is in C/Assembly, and CSCI 2600 is in Java. For each of the courses you have taken, 
             please specify the letter grade you earned in the course at RPI (or select "AP" if you 
             earned AP credit for CSCI 1100).</div>'''),
            HTML('''<div class = 'textline'> Note that you cannot be a mentor for a course you will be taking in the same semester or for a course
            you plan to take in the future. In some cases, you are allowed to mentor for courses you have never taken;
            be sure to describe equivalent courses or experiences in the general comments textbox further below.
            </div>'''),
            HTML(""" <div class = 'vspacewithline'> </div>"""),
            course_layout,
            HTML("</fieldset>"),
        )
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.add_input(Button('prev', 'Prev', onclick="window.history.go(-1); return false;"))
        self.helper.add_input(Submit('next', 'Next'))


class MentorApplicationfoForm_step4(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MentorApplicationfoForm_step4, self).__init__(*args, **kwargs)  
        self.helper = FormHelper()
        self.fields["pref_order"] = forms.CharField(max_length=10000)
        self.fields["pref_order"].required = False
        
        self.helper.layout = Layout(
            HTML('== COURSE PREFERENCE =='),

            HTML("<fieldset>"),
            HTML('''<div class = 'textline'> Select the courses you would like to mentor and the courses 
            you do not prefer. For the course you would like to mentor, please change their rankings by
            <strong style = 'color: red;'> dragging </strong> the courses. 
            #1 means the highest prioity for you to mentor, and #2 means the second priority...etc. 
            </div>'''),
            HTML('''<div class = 'textline'> Your ranking will help us to decide your position.
            </div>'''),

            HTML(""" <div class = 'vspacewithline'> </div>"""),

            # Ranking UI here
            HTML('''
            <div class ="col-md-6">
                <div class = 'panel panel-default'>
                    <div class="panel-heading">
                        <b> Courses Prefer to Mentor: &nbsp </b>
                        <button onclick="VoteUtil.clearAll(); return false;" class="btn btn-primary  reset-button" style="background"> Clear </button>
                    </div>

                    <div class="panel-body"">
                        <ul id="left-sortable" class = "sortable-ties">
                            {% for course in pref_courses %}
                            {% if course %}       
                            <ul class="course_choice" >
                                <!-- Display the tier number -->
                                    <div class="c_tier">{{ forloop.counter }}</div>
                                    <li class="course-element" id = "{{ course.name }}" type = "{{ course.name }}">
                                &nbsp {{ course.subject }} {{ course.number }}  &nbsp<strong> {{course.name }}</strong>
                                    </li>
                                </ul>
                            {% endif %}
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
            <div class ="col-md-6">
                <div class = 'panel panel-default'>
                    <div class="panel-heading">
                        <b> Courses <strong style = "color:red;">NOT</strong> Prefer to Mentor: &nbsp </b>
                        <button onclick="VoteUtil.moveAll(); return false;" class="btn btn-primary move-all-button" >
                        Move All
                        </button>
                    </div>

                    <div class="panel-body"">
                        <ul id="right-sortable">
                            {% for course in not_pref_courses %}
                            {% if course %}       
                            <ul class="course_choice2" id="{{ prev|add:1 }}" onclick="VoteUtil.moveToPref(this)">
                                <li class="course-element" id = "{{ course.name }}" type = "{{ course.name }}">
                                &nbsp {{ course.subject }} {{ course.number }}  &nbsp<strong> {{course.name }}</strong>
                                </li>
                            </ul>
                            {% endif %}
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
                '''),
            # HTML part to store thr rankings
            Field('pref_order', id='pref_order', css_class = 'pref_order', type = 'hidden'),
            HTML("</fieldset>"),
        )
        self.helper.form_method = 'POST'
        self.helper.add_input(Button('prev', 'Prev', onclick="window.history.go(-1); return false;"))
        self.helper.add_input(Submit('next', 'Next', onclick="VoteUtil.submitPref();"))
        
# Time slots availble for students
class MentorApplicationfoForm_step5(ModelForm):
    class Meta:
        model = Mentor
        fields = ( 'other_times',)
        widgets = { 
            #'time_slots': forms.CheckboxSelectMultiple(),
            'other_times': forms.Textarea(attrs={'cols': 100, 'rows': 8})
        }

    def __init__(self, *args, **kwargs):
        super(MentorApplicationfoForm_step5, self).__init__(*args, **kwargs)  
        self.helper = FormHelper()
        
        time_slots_choices = (
                     ('M_4:00-4:50PM',      'M 4:00-4:50PM'),
                     ('M_4:00-5:50PM',      'M 4:00-5:50PM'),
                     ('M_5:00-5:50PM',      'M 5:00-5:50PM'),
                     ('M_6:00-6:50PM',      'M 6:00-6:50PM'),
                     ('T_10:00-11:50AM',    'T 10:00-11:50AM'),
                     ('T_12:00-1:50PM',     'T 12:00-1:50PM'),
                     ('T_2:00-3:50PM',      'T 2:00-3:50PM'),
                     ('T_4:00-4:50PM',      'T 4:00-4:50PM'),
                     ('T_5:00-5:50AM',      'T 5:00-5:50AM'),
                     ('T_6:00-6:50PM',      'T 6:00-6:50PM'),
                     ('W_10:00-11:50AM',    'W 10:00-11:50AM'),
                     ('W_12:00-1:50PM',     'W 12:00-1:50PM'),
                     ('W_2:00-3:50PM',      'W 2:00-3:50PM'),
                     ('W_4:00-4:50PM',      'W 4:00-4:50PM'),
                     ('W_5:00-5:50AM',      'W 5:00-5:50AM'),
                     ('W_6:00-6:50PM', '     W 6:00-7:50PM'),
                     ('T_4:00-5:50AM',      'T 4:00-5:50AM'),
                     ('T_6:00-6:50PM',      'T 6:00-7:50PM'),
        )
        self.fields["time_slots"] = forms.MultipleChoiceField(
            choices=time_slots_choices, 
            label=False, 
            required=False,
            widget=forms.CheckboxSelectMultiple()
            ) 
        
        
        self.helper.layout = Layout(
            HTML('== SCHEDULING =='),
            HTML("<fieldset>"),
            HTML(''' <div class="textline"> Indicate your availability for the 
            Spring 2020 semester by carefully checking all boxes that apply. The more boxes you check,
             the more likely you will be a mentor. Note that there is overlap in some of the days/times listed below.</div>'''),
            Div("time_slots"),
            HTML(""" <div class = 'vspacewithline'> </div>"""),
            HTML(''' <div class="textline">Please list other days/times of additional availability. The more days/times you are 
            available, the more likely you will be selected as a mentor. <strong>Do not leave this blank.</strong></div>'''),
            Field('other_times', style = "width:100%"),
            HTML("</fieldset>"),
        )
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.add_input(Button('prev', 'Prev', onclick="window.history.go(-1); return false;"))
        self.helper.add_input(Submit('next', 'Next', onclick="VoteUtil.submitPref();"))



class MentorApplicationfoForm_step6(ModelForm):
    class Meta:
        model = Mentor
        fields = ( 'relevant_info', )
        widgets = { 
            'relevant_info': forms.Textarea(attrs={'cols': 100, 'rows': 8})
        }

    def __init__(self, *args, **kwargs):
        super(MentorApplicationfoForm_step6, self).__init__(*args, **kwargs)  
        self.helper = FormHelper()

        self.fields["relevant_info"] = forms.CharField(widget=forms.Textarea(attrs={'cols': 100, 'rows': 8}))
        self.helper.layout = Layout(
            HTML('== ADDITIONAL INFOMATION =='),
            HTML("<fieldset>"),
            HTML('''<div class = 'textline'> Please provide any other relevant information about yourself in the space below, including your mentoring preferences (i.e.,&nbsp;which courses you'd prefer to mentor, which courses you'd prefer not to mentor, other extracurricular CS activities you're involved with, etc.). <strong>Do not leave this blank.</strong></div>'''),
            Field('relevant_info', style = "width:100%"),
            HTML(""" <div class = 'vspacewithline'> </div>"""),

            HTML('''<div class = 'textline'>  After you choose to submit, you can save your profile and change it if needed at any time after. </div>'''),

            HTML("</fieldset>"),
        )
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.add_input(Button('prev', 'Prev', onclick="window.history.go(-1); return false;"))
        self.helper.add_input(Submit("save and submit", "Save and Submit"))

'''
# DEPRECATED 
class MentorApplicationfoForm(ModelForm):
    class Meta:
        model = Mentor
        #fields = '__all__' 
        fields = (  'RIN', 
                    'first_name', 
                    'last_name',
                    'GPA',
                    'email',
                    'phone',
                    'recommender',
                    'compensation',
                )
         
        help_texts = {
            'RIN': _(' *Required'),          
            'first_name': _(' *Required'),
            'last_name': _(' *Required'),
            'GPA': _(' *Required'),
            'email': _(' *Required'),
            'phone': _(' *Required'),
            'recommender': _(' *Required'),
        }
        
        widgets = {
            'RIN': forms.TextInput(attrs={'placeholder': ' 661680100'}),
            'GPA': forms.TextInput(attrs={'placeholder': ' 3.6'}),
            'email': forms.TextInput(attrs={'placeholder': ' xxx@rpi.email'}),
            'phone': forms.TextInput(attrs={'placeholder': ' 5185941234'}),
        }
    def __init__(self, *args, **kwargs):
        super(MentorApplicationfoForm, self).__init__(*args, **kwargs)
        #self.fields["course_pref"].required = False
        
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        #self.helper.form_action = 'applyfunc1'
        courses = Course.objects.all()
        course_layout = Div()
        
        # Add courses fields
        for course in courses:          
            course_layout.append(HTML("<div class = 'course_block'>"))   
            course_layout.append( HTML("<div class = 'course_title'>" + course.subject +" "+ course.number +" "+ course.name + "</div>") )
            grades = (
                     ('a', 'A'),
                     ('a-', 'A-'),
                     ('b+', 'B+'),
                     ('b', 'B'),
                     ('b-', 'B-'),
                     ('c+', 'C+'),
                     ('c', 'C'),
                     ('c-', 'C-'),
                     ('d+', 'D+'),
                     ('d', 'D'),
                     ('f', 'F'),
                     ('p', 'Progressing'),
                     ('n', 'Not Taken'),
                     )
            choices_YN = (
                    ('Y', 'YES'),
                    ('N', 'NO'),
            )
            self.fields[course.name+ "_grade"] = forms.ChoiceField(
                choices = grades, 
                label = "Grade on this course:",
            ) 
            #self.initial[course.name+ "_grade"] = 'n'

            self.fields[course.name+ "_exp"] = forms.ChoiceField(choices = choices_YN, label = 'Have you mentored this class before? ')
            #self.initial[course.name+ "_exp"] = 'N'

            course_layout.append(Field(course.name+ "_grade", label_class = "long_label"))
            #course_layout.append(HTML('<br></br>'))
            course_layout.append(InlineRadios(course.name+ "_exp"))
            course_layout.append(HTML("</div>"))   

        # Time slot choices
        SCHEDULING = (
                    ('M1', 'YES'),
                    ('M2', 'NO'),
            )
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup('== PERSONAL INFORMATION ==',
                    HTML("<fieldset>"),
                    Field('RIN', 'first_name', 'last_name', 'email', 'phone', 'GPA', css_class = ""),
                    HTML("""
                    <div class = 'inputline'>Please provide the name of someone in the CS Department who can recommend you. You are encouraged, but not required, to contact this person.
                    </div>"""),
                    HTML("""
                    <div class = 'inputline'>Please provide only a name here (describe additional circumstances in the freeform textbox below).</div>
                    """),
                    Field('recommender', css_class = "inputline"),
                    HTML("</fieldset>"),
                ),

                AccordionGroup('== COMPENSATION AND RESPONSIBILITIES ==',
                    HTML("<fieldset>"),
                    HTML("""
                    <div class = "inputline">
                        We currently have funding for a fixed number of paid programming mentors. Therefore, if you apply for pay, you may be asked to work for credit instead. Course credit counts as a graded 1-credit or 2-credit free elective. In general, if you work an average of 1-3 hours per week, you will receive 1 credit; if you average 4 or more hours per week, you will receive 2 credits. Note that no more than 4 credits may be earned as an undergraduate (spanning all courses and all semesters). Please do not apply for credit if you have already earned 4 credits as a mentor; apply only for pay.
                    </div>
                    """),
                    Field('compensation', css_class = ""),
                    HTML("""
                    <div class = "inputline">
                        For a paid position, you <strong>must</strong> follow
                        the given instructions to ensure you are paid; otherwise, 
                        another candidate will be selected.  More specifically, you 
                        will be required to have a <strong>student employment card</strong>.
                        This requires you to have a federal I-9 on file.  Bring appropriate 
                        identification with you to Amos Eaton&nbsp;109 if this is your first 
                        time working for RPI;
                    </div>
                    """),
                    HTML("</fieldset>"),
                ),  

                AccordionGroup('== COURSE SELECTIONS ==',
                    HTML("<fieldset>"),
                    course_layout,
                    HTML("</fieldset>"),
                ),

                AccordionGroup('== COURSE RANKINGS ==',
                    HTML("<fieldset>"),

                    HTML(''Please rank the courses which you prefer to mentor, #1 means the highest prioity, and #2 means the second priority...etc. This will help us to allocate your position.''),

                    HTML(''<ul id="left-sortable" class = "sortable-ties">
                                <div class="empty"></div> 
                                {% for course in courses %}
                                {% if course %}       
                                <ul class="course_choice" >
                                <!-- Display the tier number -->
                                    <div class="tier two">#{{ forloop.counter }}</div>
                                    <li class="course-element" id = "{{ course.name }}" type =
                                     "{{ course.name }}">
                                        {{ course.subject }} {{course.number}}
                                    </li>
                                </ul>
                                {% endif %}
                                {% endfor %}
                            </ul>
                            ''),
                    HTML('' 
                    <input type="hidden" id="pref_order" class="pref_order" name="pref_order" value=""/>
                    <input type="hidden" id="record_data" class="record_data" name="record_data" value=""/>

                    ''),
                    HTML("</fieldset>"),
                ),
                
                AccordionGroup('== SCHEDULING ==',
                    HTML("<fieldset>"),
                    HTML("Time slot plugin here"),
                    HTML("</fieldset>"),
                ),
            )
        )
        self.helper.form_method = 'POST'
        self.helper.label_class = "my_label"
        self.helper.add_input(Submit('submit', 'Submit', onclick="VoteUtil.submitPref();"))
        
    # Overide the save func
    def save(self, *args, **kwargs):
        new_applicant = Mentor()
        new_applicant.RIN = self.cleaned_data["RIN"]
        new_applicant.first_name = self.cleaned_data["first_name"]
        new_applicant.last_name = self.cleaned_data["last_name"]
        new_applicant.GPA = self.cleaned_data["GPA"]
        new_applicant.phone = self.cleaned_data["phone"]
        new_applicant.compensation = self.cleaned_data["compensation"]

        # create a dictionary to store a list of preference
        pref = Dict()
        pref.name = new_applicant.RIN
        pref.save()
            
        new_applicant.course_pref = pref
        new_applicant.save()
        #orderStr = self.cleaned_data["pref_order"]
        
        # Save Grades on the course average
        for course in Course.objects.all():
            course_grade = course.name + "_grade"
            course_exp   = course.name + "_exp"

            new_grade         = Grade()
            new_grade.student = new_applicant
            new_grade.course  = course
            new_grade.student_grade = self.cleaned_data[course_grade] # Grade on this course
            if (self.cleaned_data[course_exp] == 'Y'): # Mentor Experience
                new_grade.mentor_exp = True
            else:
                new_grade.mentor_exp = False

            # if the student has failed the class, or is progressing, we consider he did not take the course
            if (new_grade.student_grade != 'p' and new_grade.student_grade != 'n' and new_grade.student_grade != 'f'):
                new_grade.have_taken = True
            else:
                new_grade.have_taken = False
            new_grade.save()
            print(new_grade.course.name + ": " + new_grade.student_grade.upper())

        return new_applicant

'''