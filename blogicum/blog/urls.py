from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path(
        'posts/<int:pk_post>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryListView.as_view(),
        name='category_posts'
    ),
    path(
        'posts/<int:pk_post>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:pk_post>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:pk_post>/delete_comment/<int:pk_comment>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/<int:pk_post>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk_post>/edit_comment/<int:pk_comment>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'profile/edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<slug:username>/',
        views.ProfileListView.as_view(),
        name='profile'
    ),
]
