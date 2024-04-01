from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

from notes.forms import NoteForm

User = get_user_model()


class TestNotesListPage(TestCase):
    """Класс тестов страницы списка заметок."""

    NOTES_LIST_URL = reverse('notes:list')
    NOTES_COUNT = 5

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных."""
        cls.author = User.objects.create(username='Василёк')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_author = User.objects.create(username='Ромашка')
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)
        all_notes = []
        for index in range(1, cls.NOTES_COUNT+1):
            note = Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'zametka_{index}'
            )
            all_notes.append(note)
        Note.objects.bulk_create(all_notes)

    def test_context(self):
        """Заметка передаётся в контекст страницы со списком заметок."""
        response = self.author_client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        author_note = Note.objects.get(id=self.NOTES_COUNT)
        self.assertIn(author_note, object_list)

    def test_author_notes_not_in_list_another_author(self):
        """Заметка автора не попадает в список заметок другого автора."""
        Note.objects.create(
            title='Задачка',
            text='Найди решение задачки',
            author=self.another_author
        )
        response = self.another_author_client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        author_notes = Note.objects.filter(author=self.author)
        for page_object in object_list:
            with self.subTest(page_object=page_object):
                self.assertFalse(author_notes.filter(
                    author=page_object.author).exists())
        for note in author_notes:
            with self.subTest(note=note):
                self.assertFalse(object_list.filter(
                    author=note.author).exists())


class TestNoteAddEdit(TestCase):
    """Класс тестов добавления и редактирования заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных."""
        cls.author = User.objects.create(username='Розочка')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.add_url = reverse('notes:add')

    def test_author_has_add_form(self):
        """Тестирование наличия формы добавления заметки."""
        response = self.author_client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_author_has_edit_form(self):
        """Тестирование наличия формы редактирования заметки."""
        note = Note.objects.create(
            title='Цветочки',
            text='Пора сажать цветочки',
            author=self.author
        )
        edit_url = reverse('notes:edit', args=(note.slug,))
        response = self.author_client.get(edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
