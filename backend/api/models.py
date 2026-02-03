from django.db import models
from decimal import Decimal, ROUND_HALF_UP


class User(models.Model):
    """FC Online User Model"""
    ouid = models.CharField(max_length=255, primary_key=True)
    nickname = models.CharField(max_length=100)
    max_division = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['nickname']),
        ]

    def __str__(self):
        return f"{self.nickname} ({self.ouid})"


class Match(models.Model):
    """Match Record Model"""
    RESULT_CHOICES = [
        ('win', 'Win'),
        ('lose', 'Lose'),
        ('draw', 'Draw'),
    ]

    # Auto-incrementing primary key (Django will create 'id' automatically)
    match_id = models.CharField(max_length=255)  # Removed primary_key=True
    ouid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches')
    match_date = models.DateTimeField()
    match_type = models.IntegerField()
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    goals_for = models.IntegerField()
    goals_against = models.IntegerField()
    possession = models.IntegerField()
    shots = models.IntegerField()
    shots_on_target = models.IntegerField()
    pass_success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    opponent_nickname = models.CharField(max_length=100, null=True, blank=True)
    raw_data = models.JSONField()

    class Meta:
        db_table = 'matches'
        ordering = ['-match_date']
        unique_together = ['match_id', 'ouid']  # Same match can exist for different users
        indexes = [
            models.Index(fields=['ouid', '-match_date']),
            models.Index(fields=['match_type']),
            models.Index(fields=['match_id']),  # Index for match_id queries
        ]

    def __str__(self):
        return f"{self.match_id} - {self.ouid.nickname} ({self.result})"


class ShotDetail(models.Model):
    """Shot Detail Model for Heatmap"""
    RESULT_CHOICES = [
        ('goal', 'Goal'),
        ('on_target', 'On Target'),
        ('off_target', 'Off Target'),
        ('blocked', 'Blocked'),
    ]

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='shot_details')
    shooter_spid = models.BigIntegerField(null=True, blank=True)  # Player who took the shot
    assist_spid = models.BigIntegerField(null=True, blank=True)  # Player who made the assist (-1 = no assist)
    x = models.DecimalField(max_digits=5, decimal_places=4)
    y = models.DecimalField(max_digits=5, decimal_places=4)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    shot_type = models.IntegerField()  # 1=normal, 3=header, 6=volley, 7=freekick, 8=penalty, etc.
    hit_post = models.BooleanField(default=False)  # Shot hit the post/bar
    in_penalty = models.BooleanField(default=False)  # Shot taken inside penalty box
    goal_time = models.IntegerField(default=0)  # Time in seconds when shot occurred
    assist_x = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    assist_y = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'shot_details'
        indexes = [
            models.Index(fields=['match', 'result']),
            models.Index(fields=['match', 'goal_time']),
        ]

    _COORD_QUANT = Decimal('0.0001')  # 4 decimal places

    def save(self, *args, **kwargs):
        """Round coordinate fields to exactly 4 decimal places before persisting."""
        for field_name in ('x', 'y', 'assist_x', 'assist_y'):
            val = getattr(self, field_name)
            if val is not None:
                setattr(self, field_name,
                        Decimal(str(val)).quantize(self._COORD_QUANT, rounding=ROUND_HALF_UP))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shot at ({self.x}, {self.y}) - {self.result}"


class UserStats(models.Model):
    """Aggregated User Statistics Model"""
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]

    ouid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stats')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    total_matches = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    draws = models.IntegerField()
    avg_possession = models.DecimalField(max_digits=5, decimal_places=2)
    avg_shots = models.DecimalField(max_digits=5, decimal_places=2)
    avg_goals = models.DecimalField(max_digits=5, decimal_places=2)
    shot_accuracy = models.DecimalField(max_digits=5, decimal_places=2)
    xg = models.DecimalField(max_digits=5, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_stats'
        unique_together = ['ouid', 'period']
        indexes = [
            models.Index(fields=['ouid', 'period']),
        ]

    def __str__(self):
        return f"{self.ouid.nickname} - {self.period}"


class PlayerPerformance(models.Model):
    """Individual Player Performance Model"""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_performances')
    user_ouid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_performances', null=True)  # Which user this player belongs to
    spid = models.BigIntegerField()  # Player Season ID (seasonId * 1000000 + playerId)
    player_name = models.CharField(max_length=100)
    season_id = models.IntegerField(null=True, blank=True)  # Extracted season ID
    season_name = models.CharField(max_length=100, null=True, blank=True)  # Season className from metadata

    # Position and grade
    position = models.IntegerField()
    grade = models.IntegerField()

    # Core metrics
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)

    # Shooting stats (from Nexon API shoot data)
    shots = models.IntegerField(default=0)  # shootTotal
    shots_on_target = models.IntegerField(default=0)  # effectiveShootTotal
    shots_off_target = models.IntegerField(default=0)  # calculated
    shots_woodwork = models.IntegerField(default=0)  # shootOutScore

    # Passing stats (from Nexon API pass data)
    pass_attempts = models.IntegerField(default=0)  # passTry
    pass_success = models.IntegerField(default=0)  # passSuccess
    short_pass_attempts = models.IntegerField(default=0)  # shortPassTry
    short_pass_success = models.IntegerField(default=0)  # shortPassSuccess
    long_pass_attempts = models.IntegerField(default=0)  # longPassTry
    long_pass_success = models.IntegerField(default=0)  # longPassSuccess
    through_pass_attempts = models.IntegerField(default=0)  # throughPassTry
    through_pass_success = models.IntegerField(default=0)  # throughPassSuccess

    # Advanced passing (may not be in API, set null=True)
    key_passes = models.IntegerField(default=0, null=True, blank=True)
    crosses = models.IntegerField(default=0, null=True, blank=True)
    cross_success = models.IntegerField(default=0, null=True, blank=True)
    forward_passes = models.IntegerField(default=0, null=True, blank=True)

    # Dribbling stats (from Nexon API dribble data)
    dribble_attempts = models.IntegerField(default=0)  # dribbleTry
    dribble_success = models.IntegerField(default=0)  # dribbleSuccess
    dribble_stops = models.IntegerField(default=0, null=True, blank=True)  # 드리블 저지

    # Defensive stats (from Nexon API defence data)
    tackle_attempts = models.IntegerField(default=0)  # tackleTry
    tackle_success = models.IntegerField(default=0)  # tackleSuccess (renamed from tackles)
    block_attempts = models.IntegerField(default=0)  # blockTry
    blocks = models.IntegerField(default=0)  # block
    interceptions = models.IntegerField(default=0, null=True, blank=True)  # not in API
    fouls = models.IntegerField(default=0, null=True, blank=True)  # not in API

    # Aerial stats (from Nexon API aerialSuccess)
    aerial_success = models.IntegerField(default=0)  # aerialSuccess (removed aerial_attempts as API doesn't provide)

    # Goalkeeper specific stats (calculated from match data)
    saves = models.IntegerField(default=0, null=True, blank=True)  # calculated
    opponent_shots = models.IntegerField(default=0, null=True, blank=True)  # from opponent data
    goals_conceded = models.IntegerField(default=0, null=True, blank=True)  # from match result
    errors_leading_to_goal = models.IntegerField(default=0, null=True, blank=True)  # not in API

    # Expected goals (xG) - calculated or null
    xg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    xg_against = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # for GK

    # Calculated percentage fields
    pass_success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shot_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dribble_success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tackle_success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    long_pass_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    short_pass_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Cards (from Nexon API yellowCards, redCards)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'player_performances'
        indexes = [
            models.Index(fields=['match', '-rating']),
            models.Index(fields=['spid']),
        ]

    def save(self, *args, **kwargs):
        """Calculate percentage fields before saving"""
        # Pass success rate
        if self.pass_attempts > 0:
            self.pass_success_rate = round((self.pass_success / self.pass_attempts) * 100, 2)

        # Short pass accuracy
        if self.short_pass_attempts > 0:
            self.short_pass_accuracy = round((self.short_pass_success / self.short_pass_attempts) * 100, 2)

        # Long pass accuracy
        if self.long_pass_attempts > 0:
            self.long_pass_accuracy = round((self.long_pass_success / self.long_pass_attempts) * 100, 2)

        # Shot accuracy
        if self.shots > 0:
            self.shot_accuracy = round((self.shots_on_target / self.shots) * 100, 2)

        # Dribble success rate
        if self.dribble_attempts > 0:
            self.dribble_success_rate = round((self.dribble_success / self.dribble_attempts) * 100, 2)

        # Tackle success rate
        if self.tackle_attempts > 0:
            self.tackle_success_rate = round((self.tackle_success / self.tackle_attempts) * 100, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player_name} ({self.rating}) - {self.match.match_id}"
