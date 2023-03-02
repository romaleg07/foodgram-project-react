from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (ChangePasswordSerializer, SubscribeSerializer,
                             UserIncludeSerializer, UsersSerializer)
from foodgram.core.pagination import PageNumberLimitPagination

from .models import Subscribe, User


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = PageNumberLimitPagination
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    http_method_names = ['get', 'post', 'delete', 'head']

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(self.queryset, pk=pk)
        serializer = SubscribeSerializer(
            context={
                'request': request,
                'author': author
            },
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user,
            author=author
        )
        headers = self.get_success_headers(serializer.data)
        response = UserIncludeSerializer(
            author, context={'request': request}
        )
        return Response(
            response.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(self.queryset, pk=pk)
        get_object_or_404(
            Subscribe, author=author, user=self.request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        subscribtions = self.queryset.filter(
            subscribed__user=self.request.user
        )
        page = self.paginate_queryset(subscribtions)

        if not page:
            serializer = UserIncludeSerializer(
                subscribtions, many=True, context={'request': request}
            )
            return Response(serializer.data)

        serializer = UserIncludeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


@action(detail=False, methods=['get'])
class MeViewSet(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UsersSerializer
    pagination_class = None

    def get_object(self):
        username = self.request.user.username
        return get_object_or_404(User, username=username)

    def perform_update(self, serializer):
        serializer.save()


class SetNewPasswordUser(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    def create(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            if not self.object.check_password(
                serializer.data.get("current_password")
            ):
                return Response(
                    {"current_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            return Response(status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
