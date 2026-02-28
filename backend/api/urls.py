from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, MatchViewSet, UserStatsViewSet,
    get_tier_info, send_support_message, search_players, opponent_dna,
    visitor_count,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'stats', UserStatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
    path('tier-info/', get_tier_info, name='tier-info'),
    path('support/', send_support_message, name='support'),
    path('search-players/', search_players, name='search-players'),
    path('opponent-dna/', opponent_dna, name='opponent-dna'),
    path('visitor-count/', visitor_count, name='visitor-count'),
]
