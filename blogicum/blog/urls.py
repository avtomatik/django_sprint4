from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path('', views.index, name='index'),
    path(
        'posts/<int:pk_post>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:pk_post>/edit_comment/<int:pk_comment>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
]
