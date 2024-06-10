from django import forms

from .models import Comment, Post, User


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea({'rows': '3'})
        }


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'text': forms.Textarea({'rows': '5'}),
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
