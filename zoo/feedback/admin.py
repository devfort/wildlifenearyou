from django.contrib import admin

from models import Feedback

admin.site.register(Feedback,
    list_display = (
        'created', 'status', 'body', 'notes', 'from_page', 'user', 'email',
    ),
    list_filter = ('status', 'created'),
    list_editable = ('status',)
)
