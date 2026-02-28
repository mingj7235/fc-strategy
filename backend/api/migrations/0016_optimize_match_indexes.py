from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_sitevisit_and_more'),
    ]

    operations = [
        # ── Match indexes ──
        # Remove old individual indexes
        migrations.RemoveIndex(
            model_name='match',
            name='matches_ouid_id_f1271b_idx',  # (ouid, -match_date)
        ),
        migrations.RemoveIndex(
            model_name='match',
            name='matches_match_t_c89247_idx',  # (match_type)
        ),
        migrations.RemoveIndex(
            model_name='match',
            name='matches_match_i_fa7ee3_idx',  # (match_id)
        ),
        # Add new composite indexes
        migrations.AddIndex(
            model_name='match',
            index=models.Index(
                fields=['ouid', 'match_type', '-match_date'],
                name='matches_ouid_type_date_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='match',
            index=models.Index(
                fields=['match_id', 'ouid'],
                name='matches_matchid_ouid_idx',
            ),
        ),
        # ── PlayerPerformance index ──
        # Add composite index for position-based queries (user_ouid, match, position)
        # This index may already exist from a previous manual migration.
        # Using raw SQL with IF NOT EXISTS to handle both cases safely.
        migrations.RunSQL(
            sql='CREATE INDEX IF NOT EXISTS "player_perf_user_ou_16fe5c_idx" ON "player_performances" ("user_ouid_id", "match_id", "position");',
            reverse_sql='DROP INDEX IF EXISTS "player_perf_user_ou_16fe5c_idx";',
        ),
    ]
