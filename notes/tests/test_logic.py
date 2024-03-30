from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.redirect_url = reverse('notes:success')
        cls.user = User.objects.create(username='Фунтик')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT
        }

    def test_anonymous_user_cant_create_note(self):
        """Тестирование невозможности создания заметки анонимом."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Тестирование создания заметки залогиненым пользователем."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)

    def test_transliteration_slug(self):
        """Тестирование транслитерации slug для адреса страницы заметки."""
        note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            author=self.user
        )
        transliteration_slug = note.slug
        transliteration_title = slugify(note.title)
        self.assertEqual(transliteration_slug, transliteration_title)

    def test_slug_unique(self):
        """"Тестируем уникальность slug для адреса страницы заметки."""
        first_note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            author=self.user
        )
        first_slug = first_note.slug
        second_note_data = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'author': self.user,
            'slug': first_slug
        }
        response = self.auth_client.post(self.url, data=second_note_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=first_slug + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок'
    NEW_NOTE_TITLE = 'Обновлённый заголовок'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOТE_TEXT = 'Обновлённая заметка'
    NOTE_SLUG = 'logic'
    NEW_NOTE_SLUG = 'new_logic'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Неавтор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            author=cls.author,
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOТE_TEXT,
            'slug': cls.NEW_NOTE_SLUG
        }

    def test_author_can_delete_note(self):
        """Тестирование удаления заметки автором."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_author_cant_delete_note(self):
        """Тестирование невозможности удаления заметки неавтором."""
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Тестирование редактирования заметки автором."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOТE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_not_author_cant_edit_note(self):
        """Тестирование невозможности редактирования заметки неавтором."""
        response = self.not_author_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
