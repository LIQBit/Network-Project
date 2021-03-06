from django import template

from ..models import Post

register = template.Library()


@register.simple_tag(name="is_liked")

def is_liked(post_id, user_id):
    fetched_post = Post.objects.get(pk=post_id)
    UserLikesCurrentPost = (
        fetched_post.likes.all().filter(pk=user_id).exists()
    )
    return UserLikesCurrentPost