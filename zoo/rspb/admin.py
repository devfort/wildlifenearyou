from models import RspbBirdPage
from django.contrib import admin

admin.site.register(RspbBirdPage, 
    list_display = ('name', 'species', 'teaser'),
    raw_id_fields = ('species',),
    ordering = ('name',)
)
