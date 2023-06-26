from api.paginations import StandardResultsSetPagination
from api.serializers import ShortInfoRecipe, UserInfoSerializer
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import permissions, serializers
from users.models import Follow, User


class UserRegistrationSerializer(UserSerializer):
    """User serializer for registration."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        if not self.context:
            return False
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Follow.objects.filter(
            user=user,
            following_id=obj.id
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow."""

    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.IsAuthenticated,)
    following = UserInfoSerializer(read_only=True)

    class Meta:
        model = Follow
        exclude = ('user', 'id',)

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        following_id = self.context['user_id']
        if user.id == following_id:
            raise serializers.ValidationError(
                'На самого себя подписаться нельзя.'
            )
        following_id = self.context['user_id']
        follow = Follow.objects.filter(
            user=user,
            following=following_id
        )
        if request.method == 'POST':
            if follow.exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны.'
                )
        return data

    def create(self, validated_data):
        following = get_object_or_404(User, pk=self.context['user_id'])
        return Follow.objects.create(
            user=self.context['request'].user,
            following=following
        )

    def destroy(self, user, following_id):
        following = get_object_or_404(User, pk=following_id)
        follow = Follow.objects.filter(
            user=user,
            following=following
        )
        if not follow.exists():
            raise serializers.ValidationError(
                'Вы уже отписаны.'
            )
        return follow.delete()


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""

    email = serializers.StringRelatedField(
        source='following.email',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='following.id',
        read_only=True
    )
    username = serializers.StringRelatedField(
        source='following.username',
        read_only=True
    )
    first_name = serializers.StringRelatedField(
        source='following.first_name',
        read_only=True
    )
    last_name = serializers.StringRelatedField(
        source='following.last_name',
        read_only=True
    )
    recipes = serializers.SerializerMethodField(
        source='following.recipes',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'is_subscribed',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        user = get_object_or_404(User, pk=obj.following.id)
        return user.recipes.all().count()

    def get_is_subscribed(self, obj):
        if self.context:
            user = self.context.get('request').user
            if obj.user == user:
                return True
        if obj:
            return True
        return False

    def get_recipes(self, obj):
        user = get_object_or_404(User, pk=obj.following.id)
        serializer = ShortInfoRecipe(user.recipes.all(), many=True)
        return serializer.data
