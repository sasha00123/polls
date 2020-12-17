import datetime as dt
import json
from typing import List

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    begin = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=dt.datetime.max)
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='surveys')
    submitted_users = models.ManyToManyField(get_user_model(), through='Submission', related_name='submitted_surveys',
                                             related_query_name='submitted_survey')


class Question(models.Model):
    OPEN = "open"
    SINGLE_CHOICE = "s_ch"
    MULTI_CHOICE = "m_ch"

    TYPE_CHOICES = [
        (OPEN, _("Open")),
        (SINGLE_CHOICE, _("Single-choice")),
        (MULTI_CHOICE, _("Multi-choice"))
    ]
    text = models.TextField()
    type = models.CharField(choices=TYPE_CHOICES, max_length=4)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    active = models.BooleanField(default=True, blank=True)
    users_tried = models.ManyToManyField(get_user_model(), through='Trial',
                                         related_name='answered_questions', related_query_name='answered_question')
    created = models.DateTimeField(blank=True, auto_now_add=True)

    def check_answers(self, answers):
        """
        :param answers: user answers
        :return: Whether answers are correct or not
        """
        if self.type == Question.OPEN:
            return self._check_open(answers[0])
        if self.type == Question.SINGLE_CHOICE:
            return self._check_single(answers[0])
        if self.type == Question.MULTI_CHOICE:
            return self._check_multi(answers)

    def _check_open(self, answer: str):
        """
        :param answer: User answer
        :return: Whether exists a correct option with the same value
        """
        return self.options.filter(is_correct=True, value__exact=answer).exists()

    def _check_single(self, answer: int):
        """
        :param answer: User answer
        :return: Whether exists a correct option with the same id
        """
        return self.options.filter(is_correct=True, id=answer).exists()

    def _check_multi(self, answers: List[int]):
        """
        :param answers: User answers
        :return: Whether all correct answers are provided
        """
        return set(answers) == set(map(lambda option: option.id, self.options.filter(is_correct=True)))


class Submission(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='submissions')
    created = models.DateTimeField(blank=True, auto_now_add=True)


class Trial(models.Model):
    answers = models.TextField()
    is_valid = models.BooleanField(blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='trials',
                                 related_query_name='trail')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='trials',
                             related_query_name='trail')

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='trials')
    created = models.DateTimeField(blank=True, auto_now_add=True)

    def recheck(self, save=True):
        """
        Updates is_valid, doesn't save model
        """
        self.is_valid = self.question.check_answers(json.loads(self.answers))
        if save:
            self.save()

    def save(self, **kwargs):
        self.recheck(save=False)
        super().save(**kwargs)

    class Meta:
        unique_together = ('user', 'question')


class QuestionOption(models.Model):
    value = models.CharField(max_length=255, db_index=True)
    is_correct = models.BooleanField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")

    class Meta:
        unique_together = ('question', 'value')
