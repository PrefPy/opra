from django.contrib import admin

from .models import Student, Question, Response, Item, Dictionary, KeyValuePair
from .algorithms import *

# Register your models here.

class ItemInline(admin.TabularInline):
    model = Item
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ItemInline]
    list_display = ('question_text', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['question_text']

class StudentAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name',               {'fields': ['student_name']}),
        ('Email', {'fields': ['student_email']}),
    ]
    list_display = ('student_name', 'student_email')
    search_fields = ['student_name']

def PublishAllocations(modeladmin, request, queryset):
    allocation_serial_dictatorship(queryset)
PublishAllocations.short_description = "Run allocation algorithm for these responses"

class ResponseAdmin(admin.ModelAdmin):
    list_display = ['question', 'student']
    ordering = ['question']
    actions = [PublishAllocations]

admin.site.register(Response, ResponseAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Student, StudentAdmin)