from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, \
    UpdateAPIView, CreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from api.models import Survey, Question
from api.permissions import IsAdminOrReadOnly
from api.serializers import ListCreateSurveySerializer, UpdateDetailSurveySerializer, UserDetailSerializer, \
    ChangePasswordSerializer, \
    RegisterUserSerializer, AdminQuestionSerializer, TakeSurveySerializer


class ListCreateSurvey(ListCreateAPIView):
    serializer_class = ListCreateSurveySerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Survey.objects.all()
        else:
            return Survey.objects.filter(end__gt=timezone.now())

    def perform_create(self, serializer):
        # https://github.com/encode/django-rest-framework/issues/5943
        serializer.save(creator=self.request.user)


class RetrieveUpdateDestroySurvey(RetrieveUpdateDestroyAPIView):
    queryset = Survey.objects.all()
    serializer_class = UpdateDetailSurveySerializer
    permission_classes = (IsAdminOrReadOnly,)


class RegisterUser(CreateAPIView):
    model = get_user_model()
    serializer_class = RegisterUserSerializer


class MyDetailSchema(AutoSchema):
    def get_operation_id(self, path, method):
        return "MyDetail" + method.capitalize()


class MyDetail(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserDetailSerializer
    schema = MyDetailSchema()

    def get_object(self):
        return self.request.user


class UserDetail(RetrieveUpdateAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = UserDetailSerializer


class ChangePassword(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ListCreateQuestion(ListCreateAPIView):
    queryset = Question.objects.filter(active=True)
    serializer_class = AdminQuestionSerializer
    permission_classes = (IsAdminUser,)


class RetrieveUpdateDestroyQuestion(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.filter(active=True)
    serializer_class = AdminQuestionSerializer
    permission_classes = (IsAdminUser,)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()


class TakeSurveySchema(AutoSchema):
    def get_operation_id(self, path, method):
        return "TakeSurvey" + method.capitalize()


class TakeSurvey(UpdateAPIView):
    serializer_class = TakeSurveySerializer
    queryset = Survey.objects.all()
    schema = TakeSurveySchema()
