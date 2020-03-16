from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        label='', widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'コメントを入力(200文字まで)'}),
    )
    is_anonymous = forms.BooleanField(
        label='名前を伏せてコメントする', required=False,
        help_text='<a href=/pages/guide#匿名コメント>ユーザーガイド</a>をよく読んだ上でご利用下さい'
    )

    class Meta:
        model = Comment
        fields = ('is_anonymous', 'text')


class AddPointForm(forms.Form):
    count = forms.IntegerField(
        label='', widget=forms.NumberInput(attrs={'v-model': 'pointInput', 'readonly': True, 'style': 'display:none;'}),
        min_value=1
    )
