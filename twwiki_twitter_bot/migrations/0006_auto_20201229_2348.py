# Generated by Django 3.1.4 on 2020-12-30 04:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('twwiki_twitter_bot', '0005_remove_wiki_tweet_isdatetweet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wiki_tweet',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 30, 4, 48, 48, 10873, tzinfo=utc)),
        ),
    ]
