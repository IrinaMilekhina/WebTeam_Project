from django import template

register = template.Library()


@register.simple_tag
def my_url(value, field_name, urlencode=None, order_id=None):
    url = '?{}={}'.format(field_name, value)
    if order_id:
        url = '{}&{}'.format(url, f'pk={order_id}')

    if urlencode:
        querystring = urlencode.split('&')
        if order_id:
            filtered_querystring = filter(
                lambda p: p.split('=')[0] != field_name and p.split('=')[0] != 'pk', querystring)
            encoded_querystring = '&'.join(filtered_querystring)
            url = '{}&{}'.format(url, encoded_querystring, f'pk={order_id}')
        else:
            filtered_querystring = filter(
                lambda p: p.split('=')[0] != field_name, querystring)
            encoded_querystring = '&'.join(filtered_querystring)
            url = '{}&{}'.format(url, encoded_querystring)

    return url
