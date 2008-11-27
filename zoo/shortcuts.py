from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

# Explicit shadowing of HttpResponseRedirect
Redirect = HttpResponseRedirect

def render(request, template_name, context=None, base=None):
    context = context or {}
    # Do they have a current location cookie?
    context['current_location'] = request.COOKIES.get('current_location', '')
    context['base'] = base or 'base.html'
    context['path'] = request.path
    return render_to_response(
        template_name, context, context_instance = RequestContext(request)
    )

def render_json(request, obj):
    # TODO: Check request for &callback= param, validate it, use as callback
    return HttpResponse(
        simplejson.dumps(obj, indent=2),
        content_type = 'application/javascript; charset=utf8'
    )
