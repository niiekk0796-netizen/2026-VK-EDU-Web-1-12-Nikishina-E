import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(allow_unicode=True, max_length=40, unique=True, verbose_name='Тег')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Заголовок')),
                ('text', models.TextField(max_length=5000, verbose_name='Текст')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('score', models.IntegerField(default=0, verbose_name='Рейтинг')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('tags', models.ManyToManyField(blank=True, related_name='questions', to='questions.tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=5000, verbose_name='Текст')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('score', models.IntegerField(default=0, verbose_name='Рейтинг')),
                ('accepted', models.BooleanField(default=False, verbose_name='Правильный ответ')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='questions.question', verbose_name='Вопрос')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.CreateModel(
            name='QuestionLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 'Лайк'), (-1, 'Дизлайк')], verbose_name='Оценка')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='questions.question', verbose_name='Вопрос')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка вопроса',
                'verbose_name_plural': 'Оценки вопросов',
            },
        ),
        migrations.CreateModel(
            name='AnswerLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 'Лайк'), (-1, 'Дизлайк')], verbose_name='Оценка')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='questions.answer', verbose_name='Ответ')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка ответа',
                'verbose_name_plural': 'Оценки ответов',
                'constraints': [models.UniqueConstraint(fields=('user', 'answer'), name='unique_answer_vote'), models.CheckConstraint(condition=models.Q(('value__in', [-1, 1])), name='answer_vote_value')],
            },
        ),
        migrations.AddIndex(
            model_name='answer',
            index=models.Index(fields=['question', '-score', '-created', '-id'], name='questions_a_questio_c26b03_idx'),
        ),
        migrations.AddConstraint(
            model_name='answer',
            constraint=models.UniqueConstraint(condition=models.Q(('accepted', True)), fields=('question',), name='one_accepted_answer'),
        ),
        migrations.AddConstraint(
            model_name='questionlike',
            constraint=models.UniqueConstraint(fields=('user', 'question'), name='unique_question_vote'),
        ),
        migrations.AddConstraint(
            model_name='questionlike',
            constraint=models.CheckConstraint(condition=models.Q(('value__in', [-1, 1])), name='question_vote_value'),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['-created', '-id'], name='questions_q_created_7a991f_idx'),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['-score', '-created', '-id'], name='questions_q_score_07830e_idx'),
        ),
    ]
