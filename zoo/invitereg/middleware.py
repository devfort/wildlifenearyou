from zoo.shortcuts import render
from models import InviteCode

class InviteOnlyMiddleware(object):
    allowed_paths = (
        '/account/login/',
        '/account/complete/',
        '/account/login/logo/',
        '/launchsignups/',
    )
    allowed_path_prefixes = (
        '/static/',
        '/feedback/',
        '/invitation/',
        '/admin/',
    )
    
    def process_request(self, request):
        if request.path in self.allowed_paths:
            return None
        for prefix in self.allowed_path_prefixes:
            if request.path.startswith(prefix):
                return None
        
        if not request.user.is_anonymous():
            return None
        
        cookie = request.COOKIES.get('invite_code', '').strip()
        if cookie:
            try:
                InviteCode.objects.get(code = cookie)
                return None
            except InviteCode.DoesNotExist:
                pass
        
        return render(request, 'invitereg/enter_code.html')
