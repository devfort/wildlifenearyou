from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect as Redirect

def render(request, template_name, context):
    # Do they have a current location cookie?
    context['current_location'] = request.COOKIES.get('current_location', '')
    return render_to_response(
        template_name, context, context_instance = RequestContext(request)
    )
