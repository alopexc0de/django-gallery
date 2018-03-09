from django.http import HttpResponse
from django.template import loader
from django.contrib import auth

# Usage:
# template - relative path to the template you wish to render
# request - The request object for the user
# message - An optional message to me shown to the user, set to None or ''
# context - A dictionary of arbitrary key-value combos for use in the App
def _ResponseTemplate(template, request, message='', context=None):
    if isinstance(context, dict) and \
             not (context.get('message', False)):
        context['message'] = str(message)
    elif isinstance(context, dict) and \
                 (context.get('message', False)):
        context['message'] += ' -- ' + str(message)
    else:
        context = {
            'message': str(message)
        }
    
    template = loader.get_template(str(template))
    return HttpResponse(template.render(context, request))

# Logs out a user, sending them to the login screen with an optional message and context
# Same arguments as _ResponseTemplate, except for the template
def _ForceLogout(request, message='', context=None):
    auth.logout(request)
    return _ResponseTemplate('account/login.html', request, message, context)
