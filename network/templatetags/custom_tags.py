from django import template
from django.template.defaultfilters import stringfilter

from ..models import Like

register = template.Library()

@register.simple_tag
def get_emoji_count(node, emoji_type):
    """ Gets given post's/comment's emoji type count  """

    emoji_number = [emoji_tuple[0] for emoji_tuple in Like.LIKE_TYPE_CHOICES if emoji_tuple[1] == emoji_type][0]
    return node.likes.filter(emoji_type=emoji_number).count()

@register.filter
@stringfilter
def upto(value, delimiter=None):
    """ Gets the string up to the nearest delimiter """

    return value.split(delimiter)[0]
upto.is_safe = True
