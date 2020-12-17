from behave import *
from rest_framework_simplejwt.tokens import AccessToken

from accounts.factories import UserFactory, AdminFactory

use_step_matcher("re")


@given(r"an account was created with username \"(?P<username>.+)\" and password \"(?P<password>\S+)\"")
def step_impl(context, username, password):
    context.user = UserFactory.create(username=username, password=password)
    context.path_vars.setdefault('users', [])
    context.path_vars['users'].append(context.user.id)


@given("(?P<role>user|admin) is logged in")
def step_impl(context, role):
    if role == "user":
        context.user = UserFactory()
    elif role == "admin":
        context.user = AdminFactory()
    context.path_vars.setdefault('users', [])
    context.path_vars['users'].append(context.user.id)
    context.test.client.credentials(HTTP_AUTHORIZATION=f'Bearer {AccessToken.for_user(context.user)}')


@step("user is logged out")
def step_impl(context):
    context.test.client.credentials()
