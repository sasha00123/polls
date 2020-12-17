import datetime as dt

import factory
from django.contrib.auth import get_user_model

from api.models import Survey, Question, QuestionOption


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: "user_%03d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'pass')


class AdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: "admin_%03d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'pass')

    is_staff = True


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    text = factory.Faker('sentence')
    type = factory.Iterator(list(map(lambda choice: choice[0], Question.TYPE_CHOICES)))

    @factory.post_generation
    def options(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for option in extracted:
                option.question = self
                option.save()
        else:
            QuestionOption.objects.create(question=self, value="correct", is_correct=True)
            QuestionOption.objects.create(question=self, value="incorrect", is_correct=False)


class SurveyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Survey

    title = factory.Faker('sentence')
    description = factory.Faker('paragraph')
    begin = factory.Faker('date_time_between', start_date=dt.datetime.min, end_date=dt.datetime.now())
    end = factory.Faker('date_time_between', start_date=dt.datetime.now(), end_date=dt.datetime.max)
