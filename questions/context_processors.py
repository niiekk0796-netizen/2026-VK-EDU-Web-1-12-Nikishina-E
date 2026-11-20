from django.core.cache import cache


def community(request):
    return cache.get("community", {"popular_tags": [], "best_members": []})
