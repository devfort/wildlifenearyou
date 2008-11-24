
from django.utils import simplejson
from django.http import HttpResponse

def search(request):
	"""
	"""
    q = request.GET.getlist('q')
    print q
    return HttpResponse(simplejson.dumps(request.__dict__.keys()), mimetype="text/javascript")

def newdb(request):
    q = request.GET.getlist('q')
    (r'^newdb/', "search.newdb"),
    (r'^deldb/', "search.deldb"),
    (r'^add/', "search.add"),
