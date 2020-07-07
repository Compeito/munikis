from django.http import Http404
from django.shortcuts import render, get_object_or_404

from core.utils import AltPaginationListView
from .models import Page


class PagesList(AltPaginationListView):
    paginate_by = 8
    template_name = 'pages/index.html'
    context_object_name = 'pages'

    def get_queryset(self):
        category = self.request.GET.get('category', None)
        pages = Page.objects.filter(is_published=True)
        if category:
            pages = pages.filter(category=category)
        return pages.order_by('-created_at')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['Categories'] = Page.Categories

        category = self.request.GET.get('category', None)
        if category:
            if category not in Page.Categories:
                raise Http404
            context['category'] = Page.Categories[category].label
        else:
            context['category'] = 'カテゴリを選択'
        return context


pages_list = PagesList.as_view()


def show_page(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    if not page.is_published and not request.user.is_staff:
        raise Http404
    return render(request, 'pages/show.html', {'page': page})
