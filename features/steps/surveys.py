import json

from behave import *
from django.template import Template, Context

from accounts.factories import SurveyFactory, QuestionFactory
from api.models import Survey

use_step_matcher("re")


@step(r"(?P<num>\d+) surveys created")
def step_impl(context, num):
    context.path_vars.setdefault('surveys', [])
    context.path_vars['surveys'] += SurveyFactory.create_batch(int(num), creator=context.user)


@step(r"(?P<num>\d+) surveys created with (?P<data>.*)")
def step_impl(context, num, data):
    context.path_vars.setdefault('surveys', [])
    data = Template(data).render(Context(context.path_vars))
    context.path_vars['surveys'] += SurveyFactory.create_batch(int(num), creator=context.user, **json.loads(data))


@step(r"(?P<num>\d+) questions created")
def step_impl(context, num):
    context.path_vars.setdefault('questions', [])
    context.path_vars['questions'] += QuestionFactory.create_batch(int(num), survey=Survey.objects.last())


@step(r"(?P<num>\d+) questions created with (?P<data>.*)")
def step_impl(context, num, data):
    context.path_vars.setdefault('questions', [])
    data = Template(data).render(Context(context.path_vars))
    context.path_vars['questions'] += QuestionFactory.create_batch(int(num), **{"survey": Survey.objects.first(),
                                                                                **json.loads(data)})
