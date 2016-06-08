from django.contrib import admin
from .models import *
from .algorithms import *


# ALLOCATION ALGORITHM ACTION DEFS GO HERE

# serial dictatorship admin action def
def PublishAllocations_SerialDictatorship(modeladmin, request, queryset):
    allocation_serial_dictatorship(queryset)
PublishAllocations_SerialDictatorship.short_description = "Run allocation algorithm for these responses"

# random assignment admin action def
def PublishAllocationsRandomly(modeladmin, request, queryset):
    allocation_random_assignment(queryset)
PublishAllocationsRandomly.short_description = "Run random allocation algorithm for these responses"


#limits admin change permissions
# https://gist.github.com/aaugustin/1388243
# TODO: change to allow more admin control over responses
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

# item enter fields on the question form
class ItemInline(admin.TabularInline):
    model = Item
    extra = 3

# question creation form / list view
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
        ('Follow up', {'fields': ['follow_up']}),
        ('Owner', {'fields' : ['question_owner']}),
        ('Voters', {'fields' : ['question_voters']}),
    ]
    inlines = [ItemInline]
    list_display = ('question_text', 'pub_date', 'question_owner')
    list_filter = ['pub_date']
    search_fields = ['question_text']


# response editing / viewing
class ResponseAdmin(ReadOnlyModelAdmin):
    list_display = ('user', 'question', 'timestamp')
    list_filter = ['user', 'question', 'timestamp']

    # DEFINE ALL ADDITIONAL ALLOCATION ACTIONS HERE
    actions = [PublishAllocations_SerialDictatorship, PublishAllocationsRandomly]

# register models
admin.site.register(Question, QuestionAdmin)
admin.site.register(Response, ResponseAdmin)
