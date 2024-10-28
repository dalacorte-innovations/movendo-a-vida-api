from rest_framework import serializers
from core.models import Feedback, EmailMessage

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'stars', 'comment', 'category', 'feedback_mode', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value
    
    
class EmailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailMessage
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_message(self, value):
        if len(value) > 1000:
            raise serializers.ValidationError("The message is too long. Maximum length is 1000 characters.")
        return value
