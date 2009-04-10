from django.http import HttpResponse, HttpResponseRedirect
from models import Signup

def signup(request):
    email = request.POST.get('email', '').strip()
    if '@' in email:
        Signup.objects.create(email = email)
    else:
        return HttpResponse('Invalid e-mail address: hit back and try again')
    return HttpResponseRedirect('http://wildlifenearyou.com/thanks.html')

