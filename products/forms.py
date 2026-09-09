from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', 'stars']
        widgets = {
            'body': CKEditor5Widget(config_name='default'),
        }
