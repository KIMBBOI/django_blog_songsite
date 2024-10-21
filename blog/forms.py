from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        # 아래와 같이 쓸 수도 있음.
        # exclude = ('post', 'author', 'created_at' 'modified_at',)
