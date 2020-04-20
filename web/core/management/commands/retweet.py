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
                '-from:exsy_ugomemo',
                '-filter:retweets'
            )
            tweets = tsukuriga_user.api.GetSearch(term=' '.join(terms), count=50)
            retweeted = False
            for tweet in tweets[::-1]:
                try:
                    if not tweet.retweeted:
                        tsukuriga_user.api.PostRetweet(tweet.id)
                        print(f'RT: https://twitter.com/_/status/{tweet.id}')
                        retweeted = True
                    if not tweet.user.following:
                        tsukuriga_user.api.CreateFriendship(tweet.user.id, follow=False)
                        print(f'FOLLOW: https://twitter.com/{tweet.user.screen_name}')
                    if retweeted:
                        break
                except KeyboardInterrupt:
                    break
                except:
                    pass
