from rest_framework import serializers
from .models import Article, Publisher, Newsletter, User


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model.

    This serializer converts Article instances into JSON format and
    validates incoming data for article creation and updates.

    The author field is read-only and automatically assigned based on
    the authenticated user making the request.
    """

    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """
        Meta configuration for ArticleSerializer.

        Attributes:
            model (Model): The Article model.
            fields (str): Include all fields from the model.
            extra_kwargs (dict): Makes publisher optional.
        """
        model = Article
        fields = '__all__'
        extra_kwargs = {
            'publisher': {'required': False}
        }


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for the Publisher model.

    Handles conversion between Publisher instances and JSON format.
    """

    class Meta:
        """
        Meta configuration for PublisherSerializer.
        """
        model = Publisher
        fields = '__all__'


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for the Newsletter model.

    Used to serialize newsletter data and validate input.
    """

    class Meta:
        """
        Meta configuration for NewsletterSerializer.
        """
        model = Newsletter
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Exposes only basic user information required by the API,
    including ID, username, and role.
    """

    class Meta:
        """
        Meta configuration for UserSerializer.
        """
        model = User
        fields = ['id', 'username', 'role']
