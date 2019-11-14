from django import forms
from .models import *
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

# import crispy form plugin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

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
        '''  
        help_texts = {
            'RIN': _(' *Required'),          
            'first_name': _(' *Required'),
            'last_name': _(' *Required'),
            'GPA': _(' *Required'),
            'email': _(' *Required'),
            'phone': _(' *Required'),
            'recommender': _(' *Required'),
        }
        '''
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
            self.initial[course.name+ "_grade"] = 'n'

            self.fields[course.name+ "_exp"] = forms.ChoiceField(choices = choices_YN, label = 'Have you mentored this class before? ')
            self.initial[course.name+ "_exp"] = 'N'

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

                    HTML('''Please rank the courses which you prefer to mentor, #1 means the highest prioity, and #2 means the second priority...etc. This will help us to allocate your position.'''),

                    HTML('''<ul id="left-sortable" class = "sortable-ties">
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
                            '''),
                    HTML(''' 
                    <input type="hidden" id="pref_order" class="pref_order" name="pref_order" value=""/>
                    <input type="hidden" id="record_data" class="record_data" name="record_data" value=""/>

                    '''),
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

