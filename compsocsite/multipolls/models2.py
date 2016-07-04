from .models import *
# Create your models here.
@python_2_unicode_compatible
class MultiPollQuestion(models.Model):
    class Meta:
        ordering = ['order']
    multipoll = models.ForeignKey(MultiPoll)
    question = models.ForeignKey(Question)
    order = models.PositiveIntegerField(default=0)
    def __str__(self):
        return ""
    
