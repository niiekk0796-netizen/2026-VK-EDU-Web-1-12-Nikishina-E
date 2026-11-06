from .data import BEST_MEMBERS, POPULAR_TAGS


def community(request):
    return {"popular_tags": POPULAR_TAGS, "best_members": BEST_MEMBERS}
