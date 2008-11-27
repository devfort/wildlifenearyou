from django.http import HttpResponseRedirect
from zoo.shortcuts import render
from forms import form_for_request

def submit(request):
    form_class = form_for_request(request)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            feedback = form.save(commit = False)
            feedback.from_page = request.REQUEST.get('from-page', '')
            feedback.ip_address = request.META.get('REMOTE_ADDR', '')
            feedback.user_agent = request.META.get('USER_AGENT', '')[:255]
            if not request.user.is_anonymous():
                feedback.user = request.user
            feedback.save()
            if request.is_ajax():
                template = 'feedback/thanks_ajax.html'
            else:
                template = 'feedback/thanks.html'
            return render(request, template)
    else:
        form = form_class()
    
    if request.is_ajax():
        template = 'feedback/submit_ajax.html'
    else:
        template = 'feedback/submit.html'
    
    return render(request, template, {
        'form': form,
        'from_page': request.REQUEST.get('from-page', ''),
    })
