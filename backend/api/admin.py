from django.contrib import admin
from .models import User, Match, ShotDetail, UserStats


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['ouid', 'nickname', 'max_division', 'last_updated']
    search_fields = ['nickname', 'ouid']
    list_filter = ['max_division']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['match_id', 'ouid', 'match_date', 'result', 'goals_for', 'goals_against']
    search_fields = ['match_id', 'ouid__nickname']
    list_filter = ['result', 'match_type', 'match_date']
    date_hierarchy = 'match_date'


@admin.register(ShotDetail)
class ShotDetailAdmin(admin.ModelAdmin):
    list_display = ['match', 'x', 'y', 'result', 'shot_type']
    list_filter = ['result', 'shot_type']
    search_fields = ['match__match_id']


@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ['ouid', 'period', 'total_matches', 'wins', 'losses', 'draws', 'updated_at']
    list_filter = ['period']
    search_fields = ['ouid__nickname']
