from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from .forms import CommentForm
from .models import Category, Comment, Post


def fetch_required(db_manager):
    # =========================================================================
    # TODO: Replace with Custom Manager
    # =========================================================================
    FIELDS = ('author', 'category', 'location')
    return db_manager.select_related(*FIELDS).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date').annotate(comment_count=Count('comments'))


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self) -> bool | None:
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect('blog:post_detail', self.kwargs['pk_post'])


def index(request):
    template = 'blog/index.html'
    post_list = fetch_required(Post.objects)[:settings.DEFAULT_LIMIT]
    context = {
        'post_list': post_list,
    }
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(fetch_required(Post.objects), pk=pk)
    context = {
        'post': post,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_list_or_404(fetch_required(category.posts.all()))
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, template, context)


# =============================================================================
# Comment Model CRUD Classes:
# =============================================================================


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'pk_post'
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['pk_post']
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk_post': self.kwargs['pk_post']}
        )


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'pk_post'
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['pk_post']
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk_post': self.kwargs['pk_post']}
        )
