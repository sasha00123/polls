import json

import jsonschema
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Survey, Question, QuestionOption, Trial, Submission


class RegisterUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'password', 'date_joined')


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('old_password', 'new_password')

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('id', 'value')


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    survey = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Survey.objects.all())

    def get_options(self, obj):
        if obj.type != Question.OPEN:
            return OptionSerializer(obj.options, many=True).data
        else:
            return []

    class Meta:
        model = Question
        fields = ('text', 'type', 'survey', 'options')


class AdminOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('id', 'value', 'is_correct')


class AdminQuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    options = AdminOptionSerializer(many=True)

    def validate_options(self, options):
        if len(set(map(lambda option: option.get('value'), options))) != len(options):
            raise serializers.ValidationError('Option values must be unique')
        return options

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        question = Question.objects.create(**validated_data)
        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)
        return question

    def update(self, instance, validated_data):
        if 'options' in validated_data:
            instance.options.all().delete()
            options_data = validated_data.pop('options')
        else:
            options_data = []
        question = super().update(instance, validated_data)
        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)

        # Recheck attempts if options changed
        for trial in question.trials.all():
            trial.recheck()

        return question

    class Meta:
        model = Question
        fields = ('id', 'text', 'type', 'survey', 'options')


class ListCreateSurveySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    creator = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'begin', 'end', 'creator')


class UpdateDetailSurveySerializer(ListCreateSurveySerializer):
    questions = QuestionSerializer(many=True)
    # Prevents begin field from being updated after creation
    begin = serializers.CharField(read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'begin', 'end', 'creator', 'questions')


class SubmissionSerializer(serializers.ModelSerializer):
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())

    class Meta:
        model = Submission
        fields = ('survey', 'created')


class UserDetailSerializer(serializers.ModelSerializer):
    submissions = SubmissionSerializer(many=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'submissions')


class TrialSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = Trial
        fields = ('answers', 'is_valid', 'created', 'question')


class TakeSurveySerializer(serializers.ModelSerializer):
    answers = TrialSerializer(many=True, required=True)

    def validate_answers(self, trials):
        for trial in trials:
            answers = json.loads(trial['answers'])
            try:
                jsonschema.validate(answers, {"type": "array", "items": {"type": "string"}})
            except jsonschema.exceptions.ValidationError as e:
                raise serializers.ValidationError(e.message)

            if trial['question'].type in [Question.SINGLE_CHOICE, Question.MULTI_CHOICE]:
                for answer in answers:
                    if not answer.isdigit():
                        raise ValidationError('single- and multi-choice answers should be option ids')
        return trials

    def update(self, instance, validated_data):
        trials = validated_data.pop('answers')
        answers = []
        if self.context['request'].user.is_authenticated:
            submission = Submission.objects.create(user=self.context['request'].user, survey=instance)
            for trial in trials:
                answers.append(
                    Trial.objects.create(user=self.context['request'].user, question=trial['question'],
                                         answers=trial['answers'], submission=submission)
                )
        else:
            # Allow take a survey with authentication
            for trial in trials:
                t = Trial(question=trial['question'], answers=trial['answers'])
                t.recheck(save=False)
                answers.append(t)
        instance.answers = answers
        return instance

    class Meta:
        model = Survey
        fields = ('answers',)
