from django.contrib import admin
from .models import *
from .algorithms import *

def PublishAllocations(modeladmin, request, queryset):
    allocation_serial_dictatorship(queryset)
PublishAllocations.short_description = "Run allocation algorithm for these responses"

def PublishAllocationsRandomly(modeladmin, request, queryset):
    allocation_random_assignment(queryset)
PublishAllocationsRandomly.short_description = "Run random allocation algorithm for these responses"


# https://gist.github.com/aaugustin/1388243
class ReadOnlyModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin class that prevents modifications through the admin.
    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    Source: https://gist.github.com/aaugustin/1388243
    """
    actions = None

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we  assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them.
    # def has_change_permission(self, request, obj=None):
    #     # return (request.method in ['GET', 'HEAD'] and
    #     #         super().has_change_permission(request, obj))
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False


class ItemInline(admin.TabularInline):
    model = Item
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
        ('Follow up', {'fields': ['follow_up']})
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

class ResponseAdmin(ReadOnlyModelAdmin):
    list_display = ('student', 'question', 'timestamp')
    list_filter = ['student', 'question', 'timestamp']
    actions = [PublishAllocations, PublishAllocationsRandomly]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Response, ResponseAdmin)
