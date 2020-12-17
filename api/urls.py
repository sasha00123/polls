from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from api.views import ListCreateSurvey, RetrieveUpdateDestroySurvey, UserDetail, ChangePassword, RegisterUser, \
    ListCreateQuestion, RetrieveUpdateDestroyQuestion, TakeSurvey, MyDetail

surveys = [
    path('', ListCreateSurvey.as_view()),
    path('<int:pk>', RetrieveUpdateDestroySurvey.as_view()),
]

questions = [
    path('', ListCreateQuestion.as_view()),
    path('<int:pk>', RetrieveUpdateDestroyQuestion.as_view()),
]

token = [
    path('obtain', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify', TokenVerifyView.as_view(), name='token_verify'),
]

urlpatterns = [
    path('take-survey/<int:pk>', TakeSurvey.as_view()),
    path('surveys/', include(surveys)),
    path('questions/', include(questions)),
    path('token/', include(token)),
    path('account', MyDetail.as_view()),
    path('account/<int:pk>', UserDetail.as_view()),
    path('register', RegisterUser.as_view()),
    path('set-password', ChangePassword.as_view())
]
