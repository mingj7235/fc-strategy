from rest_framework import serializers
from .models import User, Match, ShotDetail, UserStats, PlayerPerformance
from .utils.division_mapper import DivisionMapper
from nexon_api.metadata import MetadataLoader


class UserSerializer(serializers.ModelSerializer):
    tier_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['ouid', 'nickname', 'max_division', 'tier_name', 'last_updated', 'created_at']

    def get_tier_name(self, obj):
        """Convert division number to tier name"""
        if obj.max_division:
            return DivisionMapper.get_tier_name(obj.max_division)
        return None


class ShotDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShotDetail
        fields = ['id', 'x', 'y', 'result', 'shot_type', 'goal_time', 'assist_x', 'assist_y']


class MatchSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='ouid.nickname', read_only=True)
    shot_details = ShotDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            'match_id', 'ouid', 'user_nickname', 'match_date', 'match_type',
            'result', 'goals_for', 'goals_against', 'possession', 'shots',
            'shots_on_target', 'pass_success_rate', 'opponent_nickname',
            'raw_data', 'shot_details'
        ]


class MatchListSerializer(serializers.ModelSerializer):
    """Simplified serializer for match list"""
    user_nickname = serializers.CharField(source='ouid.nickname', read_only=True)

    class Meta:
        model = Match
        fields = [
            'match_id', 'user_nickname', 'match_date', 'match_type',
            'result', 'goals_for', 'goals_against', 'possession',
            'shots', 'shots_on_target', 'opponent_nickname'
        ]


class UserStatsSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='ouid.nickname', read_only=True)
    win_rate = serializers.SerializerMethodField()

    class Meta:
        model = UserStats
        fields = [
            'ouid', 'user_nickname', 'period', 'total_matches', 'wins', 'losses',
            'draws', 'win_rate', 'avg_possession', 'avg_shots', 'avg_goals',
            'shot_accuracy', 'xg', 'updated_at'
        ]

    def get_win_rate(self, obj):
        if obj.total_matches == 0:
            return 0
        return round((obj.wins / obj.total_matches) * 100, 2)


class ShotAnalysisSerializer(serializers.Serializer):
    """Serializer for enhanced shot analysis results from ShotAnalyzer"""
    total_shots = serializers.IntegerField()
    goals = serializers.IntegerField()
    on_target = serializers.IntegerField()
    off_target = serializers.IntegerField()
    blocked = serializers.IntegerField()
    shot_accuracy = serializers.FloatField()
    conversion_rate = serializers.FloatField()

    # Enhanced xG metrics
    xg_metrics = serializers.DictField()

    # Big chances
    big_chances = serializers.DictField()

    # Heatmap data
    heatmap_data = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )

    # Enhanced zone analysis
    zone_analysis = serializers.DictField()

    # Shot types breakdown
    shot_types = serializers.DictField()

    # Distance analysis
    distance_analysis = serializers.DictField()

    # Angle analysis
    angle_analysis = serializers.DictField()

    # Feedback
    feedback = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class StyleAnalysisSerializer(serializers.Serializer):
    """Serializer for enhanced play style analysis results from StyleAnalyzer"""
    total_matches = serializers.IntegerField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    draws = serializers.IntegerField()
    win_rate = serializers.FloatField()

    # Tactical patterns
    attack_pattern = serializers.CharField()
    possession_style = serializers.CharField()
    defensive_approach = serializers.CharField()
    tempo = serializers.CharField()

    # Win/Loss patterns
    win_patterns = serializers.DictField()
    loss_patterns = serializers.DictField()

    # Time-based analysis
    time_analysis = serializers.DictField()

    # Efficiency metrics
    efficiency = serializers.DictField()

    # Consistency
    consistency = serializers.DictField()

    # Comeback stats
    comeback_stats = serializers.DictField()

    # Insights
    insights = serializers.ListField(
        child=serializers.CharField()
    )


class MatchDetailSerializer(serializers.ModelSerializer):
    """Detailed match serializer including raw_data"""
    user_nickname = serializers.CharField(source='ouid.nickname', read_only=True)
    shot_details = ShotDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Match
        fields = [
            'match_id', 'ouid', 'user_nickname', 'match_date', 'match_type',
            'result', 'goals_for', 'goals_against', 'possession', 'shots',
            'shots_on_target', 'pass_success_rate', 'opponent_nickname',
            'raw_data', 'shot_details'
        ]


class StatisticsSerializer(serializers.Serializer):
    """Serializer for statistics results from StatisticsCalculator"""
    total_matches = serializers.IntegerField()
    win_rate = serializers.FloatField()
    avg_goals_for = serializers.FloatField()
    avg_goals_against = serializers.FloatField()
    avg_possession = serializers.FloatField()
    avg_shots = serializers.FloatField()
    avg_shots_on_target = serializers.FloatField()
    avg_pass_success_rate = serializers.FloatField()
    recent_form = serializers.ListField(
        child=serializers.CharField()
    )
    trends = serializers.DictField()


class PlayerPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for player performance data"""
    image_url = serializers.SerializerMethodField()
    season_img = serializers.SerializerMethodField()

    class Meta:
        model = PlayerPerformance
        fields = [
            'spid', 'player_name', 'season_id', 'season_name', 'season_img', 'position', 'grade', 'rating',
            'goals', 'assists', 'shots', 'shots_on_target', 'shot_accuracy',
            'pass_attempts', 'pass_success', 'pass_success_rate',
            'dribble_attempts', 'dribble_success', 'dribble_success_rate',
            'tackle_success', 'tackle_success_rate', 'interceptions', 'blocks',
            'aerial_success',
            'yellow_cards', 'red_cards', 'image_url'
        ]

    def get_image_url(self, obj):
        """Generate player action image URL from Nexon CDN"""
        return f"https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{obj.spid}.png"

    def get_season_img(self, obj):
        """Get season badge image URL from seasonid metadata"""
        if obj.season_id:
            return MetadataLoader.get_season_img(obj.season_id)
        return ''
