from rest_framework import serializers
from .models import *

class PostSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True, required=False)
    comments = serializers.SerializerMethodField(read_only=True)

    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments, many=True)
        return serializer.data
    
    def get_tag(self, instance):
        tags = instance.tag.all()
        return [tag.name for tag in tags]

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "comments"
        ]


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post']

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

class PostListSerializer(serializers.ModelSerializer):
    comments_cnt = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    
    def get_comments_cnt(self, instance):
        return instance.comments.count()
    
    def get_tag(self, instance):
        tags = instance.tag.all()
        return [tag.name for tag in tags]
    
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "created_at",
            "updated_at",
            "image",
            "comments_cnt",
            "tag",
            "likes",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "comments_cnt", "likes"]