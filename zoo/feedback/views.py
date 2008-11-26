from django.http import HttpResponseRedirect
from zoo.shortcuts import render
from forms import form_for_request

def submit(request):
    form_class = form_for_request(request)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            feedback = form.save(commit = False)
            feedback.from_page = request.REQUEST.get('from_page', '')
            feedback.ip_address = request.META.get('REMOTE_ADDR', '')
            if not request.user.is_anonymous():
                feedback.user = request.user
            feedback.save()
            return render(request, 'feedback/thanks.html')
    else:
        form = form_class()
    
    return render(request, 'feedback/submit.html', {
        'form': form,
        'from_page': request.REQUEST.get('from_page', ''),
        'form_class': str(repr(form_class)),
    })
