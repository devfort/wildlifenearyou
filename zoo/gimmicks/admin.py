from models import Gimmick
from django.contrib import admin

admin.site.register(Gimmick,
    raw_id_fields = ('species',)
)
