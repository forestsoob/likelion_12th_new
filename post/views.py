from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Post, Comment, Tag
from .serializers import PostSerializer, CommentSerializer, PostListSerializer, TagSerializer

from .permissions import IsOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer
    
    def get_permissions(self):
        if self.action in ["update", "create", "destroy", "partial_update"]:
            return [IsOwnerOrReadOnly()]
        return []

    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        post = serializer.instance
        self.handle_tags(post)

        return Response(serializer.data)
    
    def perform_update(self, serializer):
        post = serializer.save()
        post.tag.clear()
        self.handle_tags(post)

    def handle_tags(self, post):
        tags = [word[1:] for word in post.content.split(' ') if word.startswith('#')]
        for t in tags:
            tag, created = Tag.objects.get_or_create(name=t)
            post.tag.add(tag)
        post.save()

    @action(methods=["GET"], detail=False)
    def recommend(self, request):
        ran_post = self.get_queryset().order_by("?").first()
        ran_post_serializer = PostListSerializer(ran_post)
        return Response(ran_post_serializer.data) 
    
    @action(methods=["GET"], detail=True)
    def test(self, request, pk=None):
        test_post = self.get_object()
        test_post.click_num += 1
        test_post.save(update_fields=["click_num"])
        return Response()
    
    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes += 1
        post.save(update_fields=["likes"])
        return Response({"status": "post liked", "likes": post.likes})

    @action(methods=["GET"], detail=False)
    def top_liked(self, request):
        top_posts = Post.objects.order_by('-likes')[:3]
        serializer = PostListSerializer(top_posts, many=True)
        return Response(serializer.data)
    


#여기부터
    

class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ["update", "destroy", "partial_update"]:
            return [IsOwnerOrReadOnly()]
        return []
    


class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    # queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset
    

    #def list(self, request, post_id=None):
    #    post = get_object_or_404(Post, id = post_id)
    #    queryset = self.filter_queryset(self.get_queryset().filter(post=post))
    #    serializer = self.get_serializer(queryset, many=True)
    #    return Response(serializer.data)
    
    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id = post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data)


class TagViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "name"
    lookup_url_kwarg = "tag_name"

    def retrieve(self, request, *args, **kwargs):
        tag_name = kwargs.get("tag_name")
        tag = get_object_or_404(Tag, name=tag_name)
        posts = PostSerializer.objects.filter(tag=tag)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)