from django.db import models
from accounts.models import User
from django.utils import timezone

class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='services', blank=True)
    price = models.IntegerField()
    dead_line = models.DateField(blank=True ,auto_now=False, auto_now_add=False)
    
    def is_open(self) :
        return self.dead_line > timezone.now().date()
    

class Housing(Service):
    def __str__(self):
        return self.title
    
class Transportation(Service):
    def __str__(self):
        return self.title
    

class Team(models.Model) :
    team_name = models.CharField(max_length=50, unique=True)
    contestants = models.ManyToManyField(User, related_name='ecpcq_team', blank=True)
    coach = models.ForeignKey(User, related_name='coached_teams', on_delete=models.PROTECT, null=True)
    is_paid = models.BooleanField(default=False)
    contest = models.ForeignKey('ECPCQ', related_name='teams', on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.team_name


class ECPCQ(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    requirments = models.TextField(blank=True, null=True)
    contest_date = models.DateField(auto_now=False, auto_now_add=False)
    dead_line = models.DateField(null=False, auto_now=False, auto_now_add=False)
    
    def is_open(self) :
        return self.dead_line > timezone.now().date()
    
    def __str__(self):
        return self.title