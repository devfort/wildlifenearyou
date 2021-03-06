from zoo.accounts.openid import RegistrationConsumer
from zoo.shortcuts import render
from models import InviteCode
from django.http import HttpResponse, HttpResponseRedirect
import datetime

class InviteRegistrationConsumer(RegistrationConsumer):
    
    def do_register(self, request, message=None):
        # They need to have an invitation cookie
        try:
            invite_code = InviteCode.objects.get(
                code = request.COOKIES.get('invite_code', ''),
                claimed = False
            )
        except InviteCode.DoesNotExist:
            return self.show_message(
                request, 'No invitation code', 'You need a valid invitation'
            )
        return super(InviteRegistrationConsumer, self).do_register(
            request, message
        )
    
    def create_user(self, request, data, openid=None):
        user = super(InviteRegistrationConsumer, self).create_user(
            request, data, openid
        )
        # ... and mark their invitation code as having been used
        try:
            invite_code = InviteCode.objects.get(
                code = request.COOKIES.get('invite_code', '')
            )
            invite_code.claimed = True
            invite_code.claimed_at = datetime.datetime.now()
            invite_code.claimed_by = user
            invite_code.save()
        except InviteCode.DoesNotExist:
            pass
        return user

def enter_invite_code(request):
    if request.method == 'POST':
        return invitation(request, request.POST.get('invite', ''))
    return render(request, 'invitereg/enter_code.html')

def clear_invite_code(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('invite_code')
    return response

def invitation(request, code):
    try:
        invite_code = InviteCode.objects.get(code = code, claimed = False)
    except InviteCode.DoesNotExist:
        return render(request, 'invitereg/invalid_code.html')
    response = HttpResponseRedirect('/')
    response.set_cookie('invite_code', invite_code.code)
    return response
