from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import PAGINATE_BY
from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User


def make_comment_annotation(db_manager):
    # =========================================================================
    # TODO: Rewrite to Pipe Instead
    # =========================================================================
    return db_manager.annotate(comment_count=Count('comments'))


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect('blog:post_detail', self.kwargs['pk_post'])


class PostListView(ListView):
    """Главная страница."""

    model = Post
    paginate_by = PAGINATE_BY
    queryset = make_comment_annotation(Post.objects_tailored.all())
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
        return make_comment_annotation(
            Post.objects_tailored.filter(category=category)
        )

    def get_context_data(self, **kwargs):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()

        post_particular = get_object_or_404(Post, pk=self.kwargs['pk_post'])
        db_manager = Post.objects.all() if (
            post_particular.author == self.request.user
        ) else Post.objects_tailored.all()

        context['post'] = get_object_or_404(
            db_manager,
            pk=self.kwargs['pk_post']
        )
        context['comments'] = self.object.comments.all().select_related('post')
        return context


# =============================================================================
# Comment Model CRUD Classes:
# =============================================================================


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания комментария."""

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
    """Представление для изменения комментария."""

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
    """Представление для удаления комментария."""

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
    """Страница для публикации новых записей."""

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
    """Страница редактирования публикации."""

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
    """Страница удаления публикации."""

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


class ProfileListView(ListView):
    """Страница пользователя."""

    model = Post
    paginate_by = PAGINATE_BY
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        db_manager = Post.objects.all() if (
            self.author == self.request.user
        ) else Post.objects_tailored.all()

        FIELDS = ('author', 'category', 'location')

        return make_comment_annotation(
            db_manager.select_related(*FIELDS).filter(
                author=self.author
            )
        ).order_by(
            '-pub_date'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования профиля."""

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
