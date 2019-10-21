from django import forms

# not using right now
class ApplyForm(forms.Form):
    rin         = forms.CharField(label='rin', max_length=100)
    first_name  = forms.CharField(label='fname', max_length=100)
    last_name   = forms.CharField(label='lname', max_length=100)
    phone       = forms.CharField(label='phone', max_length=100)
    gpa         = forms.CharField(label='gpa', max_length=100)
