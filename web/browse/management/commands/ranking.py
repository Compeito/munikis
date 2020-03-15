from django.core.management.base import BaseCommand

from browse.models import Ranking
from browse.utils import safe_videos


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        Ranking.objects.all().delete()

        rankings = []
        for video in safe_videos().prefetch_related('comment_set'):
            rankings += video.calculate_rankings()
        Ranking.objects.bulk_create(rankings)
