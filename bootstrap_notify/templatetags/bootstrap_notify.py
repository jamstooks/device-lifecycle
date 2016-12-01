from django import template
from django.conf import settings
from django.contrib.messages import constants

register = template.Library()

LEVEL_LOOKUPS = {
    constants.DEBUG: 'info',
    constants.INFO: 'info',
    constants.SUCCESS: 'info',
    constants.WARNING: 'warning',
    constants.ERROR: 'danger',
}


@register.inclusion_tag('bootstrap_notify/messages.html', takes_context=True)
def show_bootstrap_messages(context):
    message_list = []
    for message in context['messages']:
        message_list.append({
            'message': message,
            'msg_class': LEVEL_LOOKUPS[message.level]})

    return {
        'message_list': message_list
    }
