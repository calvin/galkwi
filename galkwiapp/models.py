from django.db import models
from django.contrib.auth import models as auth_models
from django.utils import timezone


class User(auth_models.AbstractUser):
    tos_rev = models.DateTimeField(verbose_name='약관 동의', null=True, blank=True)
    REQUIRED_FIELDS = ['email']

POS_CHOICES = [
    ('명사', '명사'),
    ('동사', '동사'),
    ('형용사', '형용사'),
    ('부사', '부사'),
    ('대명사', '대명사'),
    ('감탄사', '감탄사'),
    ('관형사', '관형사'),
    ('특수:금지어', '특수:금지어'),
    ('특수:파생형', '특수:파생형'),
]


# word entry in dictionary
class Word(models.Model):
    # word data
    word = models.CharField(verbose_name='단어', max_length=100)
    pos = models.CharField(verbose_name='품사', max_length=100, choices=POS_CHOICES)
    props = models.CharField(verbose_name='속성', max_length=100, blank=True)
    stem = models.CharField(verbose_name='어근', max_length=100, blank=True)
    etym = models.CharField(verbose_name='어원', max_length=100, blank=True)
    orig = models.CharField(verbose_name='본딧말', max_length=100, blank=True)
    description = models.CharField(verbose_name='설명', max_length=1000, blank=True)

    def __str__(self):
        name = '%s (%s)' % (self.word, self.pos)
        return name


class Entry(models.Model):
    title = models.CharField(verbose_name='제목', max_length=100)
    latest = models.ForeignKey('Revision', related_name='revision_latest', null=True, blank=True)
    # TODO: discuss

    class Meta:
        verbose_name_plural = 'Entries'
    #     ordering = ['word', 'pos', 'valid']

    def __str__(self):
        name = '%s' % (self.title)
        return name

    def get_absolute_url(self):
        return '/entry/%d/' % (self.id)

    def update_rev(self, rev):
        self.latest = rev
        if rev.deleted:
            word = rev.parent.word
            self.title = 'OBSOLETE:%s(%s)' % (word.word, word.pos)
        else:
            word = rev.word
            self.title = '%s(%s)' % (word.word, word.pos)


REVISION_STATUS_CHOICES = [
    ('DRAFT', '편집 중'),
    ('VOTING', '투표 중'),
    ('CANCELED', '취소'),
    ('APPROVED', '허용'),
    ('REJECTED', '거절'),
    ('EXPIRED', '만료'),
]

class Revision(models.Model):
    status = models.CharField(verbose_name='상태', max_length=10, choices=REVISION_STATUS_CHOICES)
    entry = models.ForeignKey(Entry, verbose_name='단어 항목', null=True)
    parent = models.ForeignKey('self', verbose_name='이전 리비전', null=True, blank=True)
    # content or deleted
    word = models.ForeignKey(Word, verbose_name='단어 데이터', null=True, blank=True)
    deleted = models.BooleanField(verbose_name='삭제', default=False)

    comment = models.CharField(verbose_name='설명', max_length=1000, blank=True)
    user = models.ForeignKey(User, verbose_name='편집자')
    # user_text = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(verbose_name='제안 시각')

    reviewer = models.ForeignKey(User, verbose_name='리뷰어', related_name='reviewer', null=True, blank=True)
    review_comment = models.CharField(verbose_name='리뷰 설명', max_length=1000, blank=True)
    review_timestamp = models.DateTimeField(verbose_name='리뷰 시각', null=True, blank=True)

    class Meta:
        ordering = ['-timestamp', 'status']
        permissions = [
            ("can_suggest", "Can suggest a change"),
            ("can_review", "Can review a suggestion"),
        ]

    def __str__(self):
        name = '%d:' % self.id
        if self.action_is_add():
            name += 'ADD:' + str(self.word)
        elif self.action_is_remove():
            name += 'REMOVE:' + str(self.parent.word)
        elif self.action_is_update():
            name += 'UPDATE:' + str(self.word)
        return name

    def action_name(self):
        if self.parent == None:
            return 'ADD'
        else:
            if self.deleted:
                return 'REMOVE'
            else:
                return 'UPDATE'

    def action_is_add(self):
        return self.parent == None

    def action_is_remove(self):
        return self.parent != None and self.deleted

    def action_is_update(self):
        return self.parent != None and not self.deleted

    def get_absolute_url(self):
        return '/suggestion/%d/' % (self.id)

    def approve(self, reviewer, comment):
        if self.status != 'VOTING':
            return
        # FIXME: need transaction
        if self.action_is_add():
            entry = Entry()
            entry.update_rev(self)
            entry.save()
            self.entry = entry
        else:
            entry = self.entry
            entry.update_rev(self)
            entry.save()
        self.reviewer = reviewer
        self.review_comment = comment
        self.review_timestamp = timezone.now()
        self.status = 'APPROVED'
        self.save()

    def reject(self, reviewer, comment):
        self.status = 'REJECTED'
        self.reviewer = user
        self.review_comment = comment
        self.save()

    def cancel(self):
        self.status = 'CANCELED'
        self.save()
