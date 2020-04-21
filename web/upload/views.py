from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import FormView

from browse.models import Label
from .decorators import users_video_required, upload_limitation
from .forms import VideoFileUploadForm, VideoImportForm, VideoProfileForm, LabelInlineFormSet
from .importer import ImportFile, ImportFileError
from .models import Video, VideoProfile


def get_process(active_index):
    process = [
        {'title': '1. ファイル選択', 'is_active': False},
        {'title': '1-2. インポートURL入力', 'is_active': False},
        {'title': '2. 紹介文設定', 'is_active': False},
        {'title': '3. 完了！', 'is_active': False},
    ]
    process[active_index]['is_active'] = True
    return process


@login_required
@upload_limitation
def upload(request):
    form = VideoFileUploadForm()

    if request.method == 'POST':
        form = VideoFileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            video = Video.objects.create(user=request.user)
            VideoProfile.objects.create(
                video=video,
                title=request.user.name + 'さんの作品'
            )
            try:
                pure_video = form.save(commit=False)
                pure_video.video = video
                pure_video.save()
            except Exception as e:
                video.delete()
                raise e

            return redirect(f'/upload/detail/{video.slug}')

    return render(request, 'upload/form.html', {'process': get_process(0), 'form': form})


@login_required
@upload_limitation
def import_upload(request):
    form = VideoImportForm()

    if request.method == 'POST':
        form = VideoImportForm(request.POST)

        imported = None
        try:
            imported = ImportFile(user=request.user, url=form.data['url'])
        except ImportFileError as e:
            form.add_error('url', e.args[0] + ' 詳細はインポートガイドをご確認ください')

        if form.is_valid() and imported is not None:
            imported.download_file()
            imported.create_video()

            return redirect(f'/upload/detail/{imported.video.slug}')

    return render(request, 'upload/import.html', {'process': get_process(1), 'form': form})


@login_required
@users_video_required
def detail(request, slug):
    form = VideoProfileForm(request.POST or None, request.FILES or None, instance=request.video.profile)
    formset = LabelInlineFormSet(request.POST or None, instance=request.video.profile)

    for formset_form in formset.forms:
        # 描画時にN+1の挙動になるものの解決策分からず
        formset_form.fields['label'].queryset = Label.objects.filter(
            Q(is_active=True) | Q(id__in=request.video.profile.labels.all())
        )

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        return redirect(f'/upload/complete/{request.video.slug}')

    context = {
        'form': form,
        'formset': formset,
        'process': get_process(2)
    }
    return render(request, 'upload/profile.html', context)


@login_required
@users_video_required
def complete(request, slug):
    return render(request, 'upload/complete.html', {'process': get_process(3), 'video': request.video})


class Update(FormView):
    form_class = VideoFileUploadForm
    template_name = 'upload/update.html'
    extra_context = {'process': get_process(0)}

    def form_valid(self, form):
        video = self.request.video
        if hasattr(video, 'pure'):
            video.pure.delete()
        if hasattr(video, 'data'):
            video.data.delete()

        pure_video = form.save(commit=False)
        pure_video.video = video
        pure_video.save()

        video.published_at = timezone.now()
        video.type = 'updated'
        video.save()

        return redirect(f'/upload/complete/{video.slug}')


update = login_required(users_video_required(Update.as_view()))
