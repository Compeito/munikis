from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from upload.generic import VideoProfileUpdateView
from .models import Video, VideoProfile
from .importer import ImportFile, ImportFileError
from .decorators import users_video_required, upload_limitation
from .forms import VideoFileUploadForm, VideoImportForm


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
            pure_video = form.save(commit=False)
            pure_video.video = video
            pure_video.save()

            VideoProfile.objects.create(
                video=video,
                title=request.user.name + 'さんの作品'
            )

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


class Detail(VideoProfileUpdateView):
    template_name = 'upload/profile.html'

    def get_success_url(self):
        return f'/upload/complete/{self.request.video.slug}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['process'] = get_process(2)
        return context


@login_required
@users_video_required
def detail(request, slug):
    return Detail.as_view()(request, slug)


@login_required
@users_video_required
def complete(request, slug):
    return render(request, 'upload/complete.html', {'process': get_process(3), 'video': request.video})
