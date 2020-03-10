from time import sleep

from django.core.management.base import BaseCommand
from account.models import User


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        try:
            tsukuriga_user = User.objects.get(username='tsukuriga')
        except:
            return
        if tsukuriga_user.has_twitter_auth:
            terms = (
                '(',
                '("ツクリガ" filter:links)',
                'OR'
                '#tsukuriga',
                'OR'
                '(source:"tsukuriga" card_name:animated_gif)',
                ')',
                '-from:tsukuriga',
                '-from:ugo_compeito',
                '-filter:retweets'
            )
            tweets = tsukuriga_user.api.GetSearch(term=' '.join(terms), count=50)
            count = 0
            for tweet in tweets[::-1]:
                if count >= 5:
                    break
                try:
                    if not tweet.retweeted:
                        tsukuriga_user.api.PostRetweet(tweet.id)
                        print(f'RT: https://twitter.com/_/status/{tweet.id}')
                        count += 1
                    if not tweet.user.following:
                        tsukuriga_user.api.CreateFriendship(tweet.user.id, follow=False)
                        print(f'FOLLOW: https://twitter.com/{tweet.user.screen_name}')
                    sleep(5 * 60)
                except KeyboardInterrupt:
                    break
                except:
                    pass
