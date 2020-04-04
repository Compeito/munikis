import functools
import operator
import random

from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .utils import safe_videos
from .models import Ranking, Label
from core.utils import AltPaginationListView


class Home(TemplateView):
    template_name = 'browse/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'labels': self.get_labels(),
            'recent_videos': self._get_recent_videos(),
            'ranking_videos': self._get_ranking_videos(),
            'pickup_videos': self._get_pickup_videos(),
        })
        return context

    @staticmethod
    def get_labels():
        # https://docs.djangoproject.com/en/2.1/topics/db/aggregation/#order-by
        active_labels = Label.objects.filter(is_active=True)
        return active_labels.annotate(count=Count('videoprofilelabelrelation')).order_by('-count')

    @staticmethod
    def _get_recent_videos():
        recent_videos = safe_videos().order_by('-published_at')[:50]
        return sorted(recent_videos, key=lambda x: random.random())[:8]

    @staticmethod
    def _get_ranking_videos():
        return RankingList().get_queryset()[:8]

    @staticmethod
    def _get_pickup_videos():
        return safe_videos().filter(is_pickup=True).order_by('-published_at')[:6]


home = Home.as_view()


class Recent(AltPaginationListView):
    template_name = 'browse/recent.html'
    context_object_name = 'videos'
    paginate_by = 12
    extra_context = {'labels': Home.get_labels()}

    def get_queryset(self):
        return safe_videos().order_by('-published_at')


recent = Recent.as_view()


class Timeline(AltPaginationListView):
    template_name = 'browse/timeline.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        return safe_videos().filter(user__followers=self.request.user).order_by('-published_at')


timeline = login_required(Timeline.as_view())


class Search(AltPaginationListView):
    template_name = 'browse/search.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        q_list = q.split(' ')

        return safe_videos().filter(
            functools.reduce(operator.and_, (Q(profile__title__contains=item) for item in q_list)) |
            functools.reduce(operator.and_, (Q(profile__description__contains=item) for item in q_list)) |
            functools.reduce(operator.and_, (Q(user__name__contains=item) for item in q_list)) |
            functools.reduce(operator.and_, (Q(user__username__contains=item) for item in q_list))
        ).order_by('-published_at')


search = Search.as_view()


class RankingList(AltPaginationListView):
    template_name = 'browse/ranking.html'
    context_object_name = 'videos'
    paginate_by = 12

    ranking_type = 'popular'
    ranking_day = 'week'

    def get(self, request, *args, **kwargs):
        self.ranking_type = self.kwargs.get('type', self.ranking_type)
        self.ranking_day = self.kwargs.get('day', self.ranking_day)

        Ranking.raise_http404_for_sort(self.ranking_type, self.ranking_day)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            safe_videos()
                .prefetch_related('ranking_set')
                .filter(ranking__type=self.ranking_type, ranking__day=self.ranking_day)
                .order_by('-ranking__point')
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['Ranking'] = Ranking
        context['ranking_type'] = Ranking.TypeChoices[self.ranking_type]
        context['ranking_day'] = Ranking.DayChoices[self.ranking_day]
        return context


ranking = RankingList.as_view()


class LabelList(AltPaginationListView):
    template_name = 'browse/label.html'
    context_object_name = 'videos'
    paginate_by = 12

    label = None

    def get(self, request, *args, **kwargs):
        self.label = get_object_or_404(Label, slug=self.kwargs.get('slug'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return safe_videos().filter(profile__labels=self.label).order_by('-published_at')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['label'] = self.label
        context['labels'] = Home.get_labels().exclude(id=self.label.id)
        return context


label = LabelList.as_view()


class LabelIndex(AltPaginationListView):
    template_name = "browse/label_index.html"
    context_object_name = "labels"
    paginate_by = 15

    def get_queryset(self):
        return Label.objects.all().order_by('-is_active', '-id')


label_index = LabelIndex.as_view()
