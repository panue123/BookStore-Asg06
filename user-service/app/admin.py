from django.contrib import admin
from .models import UserAccount, Address, Job

admin.site.register(UserAccount)
admin.site.register(Address)
admin.site.register(Job)
