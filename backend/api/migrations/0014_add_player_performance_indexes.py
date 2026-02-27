from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_match_pass_success_rate_nullable'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='playerperformance',
            index=models.Index(
                fields=['match', 'user_ouid'],
                name='player_perf_match_user_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='playerperformance',
            index=models.Index(
                fields=['user_ouid', 'spid'],
                name='player_perf_user_spid_idx',
            ),
        ),
    ]
