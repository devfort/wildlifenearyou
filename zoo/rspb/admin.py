from models import RspbBirdPage
from django.contrib import admin
from animals.models import Species
from django.utils.safestring import mark_safe

class RspbBirdPageAdmin(admin.ModelAdmin):
    list_display = ('name', 'species_preview', 'best_guess', 'teaser')
    raw_id_fields = ('species',)
    ordering = ('name',)
    list_per_page = 20
    
    def best_guess(self, obj):
        matches = Species.objects.filter(common_name__icontains = obj.name)
        if matches:
            match = matches[0]
            return mark_safe(u'<a href="%s">%s</a>' % (
                '/admin2/rspb/rspbbirdpage/%s/?species=%s' % (
                    obj.pk, match.pk
                ), match.common_name
            ))
        else:
            return u''
    
    best_guess.allow_tags = True
    
    def species_preview(self, obj):
        return u'%s' % obj.species.all()

admin.site.register(RspbBirdPage, RspbBirdPageAdmin)
