from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(library)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Enrollment)
