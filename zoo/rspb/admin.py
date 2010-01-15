from models import RspbBirdPage
from django.contrib import admin

admin.site.register(RspbBirdPage, 
    list_display = ('name', 'teaser'),
    raw_id_fields = ('species',),
    ordering = ('name',)
)

