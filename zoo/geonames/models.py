from django.db import models

class Geoname(models.Model):
    country_code = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=10)
    place_name = models.CharField(max_length=180)
    admin_name1 = models.CharField(max_length=100, blank=True)
    admin_code1 = models.CharField(max_length=20, blank=True)
    admin_name2 = models.CharField(max_length=100, blank=True)
    admin_code2 = models.CharField(max_length=20, blank=True)
    admin_name3 = models.CharField(max_length=100, blank=True)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)
    accuracy = models.CharField(max_length=10, blank=True)
    
    def __unicode__(self):
        return u'%s (%s)' % (self.place_name, self.country_code)
    
    def for_xapian(self):
        bits = []
        for field in (
            'place_name', 'admin_name3', 'admin_name2', 'admin_name1',
            'postal_code', 'id'):
            if getattr(self, field):
                bits.append(unicode(getattr(self, field)))
        return ', '.join(bits)
    
def load_geonames():
    import os
    lines = open(
        os.path.join(os.path.dirname(__file__), 'data/GB.txt')
    ).readlines()
    fields = [f.name for f in Geoname._meta.fields[1:]]
    for line in lines:
        line = line.strip()
        if not line:
            continue
        Geoname.objects.create(
            **dict(zip(fields, line.split("\t")))
        )
