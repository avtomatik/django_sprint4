from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User

PAGINATE_BY = 10


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


class PostListView(ListView):
    """Главная страница."""

    model = Post
    paginate_by = PAGINATE_BY
    queryset = fetch_required(Post.objects)
    template_name = 'blog/index.html'


class CategoryListView(ListView):
    """Страница категории."""

    model = Post
    paginate_by = PAGINATE_BY
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return get_list_or_404(fetch_required(category.posts.all()))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class PostDetailView(DetailView):
    """Отдельная страница публикации."""

    model = Post
    pk_url_kwarg = 'pk_post'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['post'] = get_object_or_404(
            fetch_required(Post.objects),
            pk=self.kwargs['pk_post']
        )
        context['comments'] = self.object.comments.all().select_related('post')
        return context


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


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'pk_comment'
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


# =============================================================================
# Post Model CRUD Classes:
# =============================================================================


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'pk_post'
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk_post': self.kwargs['pk_post']}
        )


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'pk_post'
    template_name = 'blog/create.html'

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


# =============================================================================
# User Classes:
# =============================================================================


class ProfileListView(LoginRequiredMixin, ListView):
    """Страница пользователя."""

    model = Post
    paginate_by = PAGINATE_BY
    template_name = 'blog/profile.html'

    def get_queryset(self) -> QuerySet[Any]:
        profile = get_object_or_404(User, username=self.kwargs['username'])
        return get_list_or_404(
            fetch_required(Post.objects),
            author=profile
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )
