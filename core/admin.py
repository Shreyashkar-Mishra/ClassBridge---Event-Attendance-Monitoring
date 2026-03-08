from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Faculty,Student,Coordinator,Event,ClassLog,Absence

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Faculty)
admin.site.register(Student)
admin.site.register(Coordinator)
admin.site.register(Event)
admin.site.register(ClassLog)
admin.site.register(Absence)