from django.contrib import admin
from models import Signup

admin.site.register(Signup, list_display = ('email', 'created'))
