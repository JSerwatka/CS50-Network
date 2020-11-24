from django import template
from django.template.defaultfilters import stringfilter

from ..models import Like

register = template.Library()

# Gets given post's emoji type count
@register.simple_tag
def get_emoji_count(node, emoji_type):
    emoji_number = [emoji_tuple[0] for emoji_tuple in Like.LIKE_TYPE_CHOICES if emoji_tuple[1] == emoji_type][0]
    return node.likes.filter(emoji_type=emoji_number).count()

@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]
upto.is_safe = True