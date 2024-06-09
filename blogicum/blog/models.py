from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel
from .constants import MAX_LENGTH_CHAR, MAX_LENGTH_SLUG

User = get_user_model()


class Category(BaseModel):
    """Тематическая категория"""

    title = models.CharField('Заголовок', max_length=MAX_LENGTH_CHAR)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(BaseModel):
    """Географическая метка"""

    name = models.CharField('Название места', max_length=MAX_LENGTH_CHAR)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(BaseModel):
    """Публикация"""

    title = models.CharField('Заголовок', max_length=MAX_LENGTH_CHAR)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — можно делать отложенные '
            'публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Местоположение',
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Категория',
        null=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
