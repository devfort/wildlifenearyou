from django.contrib import admin

from models import Feedback

admin.site.register(Feedback, list_display = (
    'created', 'body', 'from_page', 'user', 'email'
))

