from django.contrib import admin

from eLearn.models import CustomUser, Course

admin.site.register(CustomUser)
admin.site.register(Course)
