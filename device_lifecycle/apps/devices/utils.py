from django.utils.crypto import get_random_string


def get_upload_to(instance, filename):

    if hasattr(instance, 'organization'):
        org = instance.organization
    else:
        org = instance.device.organization

    unique_id = get_random_string(length=16)

    return "%s/%s-%s/%s" % (
        org.slug,
        instance.__class__.__name__.lower(),
        unique_id,
        filename)
