from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect as Redirect, HttpResponse
from django.utils import simplejson

def render(request, template_name, context):
    # Do they have a current location cookie?
    context['current_location'] = request.COOKIES.get('current_location', '')
    return render_to_response(
        template_name, context, context_instance = RequestContext(request)
    )

def render_json(request, obj):
    # TODO: Check request for &callback= param, validate it, use as callback
    return HttpResponse(
        simplejson.dumps(obj, indent=2), 
        content_type = 'application/javascript; charset=utf8'
    )
