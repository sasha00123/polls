import json
from functools import partial

from behave import *
import jsonschema
from django.template import Template, Context
from jsonpath import jsonpath

from api.models import Question

use_step_matcher("re")


@when(r"the request sends (?P<method>GET|POST|PUT|PATCH|DELETE) to (?P<path>\S+)")
def step_impl(context, method, path):
    data = Template(context.text or "{}").render(Context(context.path_vars))
    path = Template(path).render(Context(context.path_vars))
    send = getattr(context.test.client, method.lower())
    if method in ['POST', 'PUT', 'PATCH']:
        context.response = send(path, data=data, content_type='application/json')
    else:
        context.response = send(path, data=json.loads(data))


@then(r"the response status is (?P<status_code>\d+)")
def step_impl(context, status_code):
    context.test.assertEqual(int(status_code), context.response.status_code)


@step(r"the response json matches")
def step_impl(context):
    jsonschema.validate(context.response.json(), json.loads(context.text))


@step('the response json at (?P<path>.*) is equal to (?P<value>.*)')
def step_impl(context, path, value):
    expected = json.loads(value)
    for found in jsonpath(context.response.json(), path):
        context.test.assertEqual(found, expected)
