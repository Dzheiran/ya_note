import pytest

from django.test.client import Client

from notes.models import Note


@pytest.fixture
def author(django_user_model):
    """Пользователь (автор)."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Пользователь (неавтор)."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Залогиненный автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Залогиненный неавтор."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def note(author):
    """Создаём заметку."""
    note = Note.objects.create(
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author,
    )
    return note

@pytest.fixture
def slug_for_args(note):
    """Получаем slug заметки."""
    return (note.slug,)
