from api.paginations import StandardResultsSetPagination
from rest_framework import permissions, response, status, viewsets
from users.models import Follow
from users.serializers import FollowSerializer, SubscriptionsSerializer


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """View to get list of follwings."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    http_method_names = ('post', 'delete', 'get',)
    lookup_field = 'user_id'

    def destroy(self, request, user_id):
        serializer = self.serializer_class
        serializer.destroy(self, request.user, user_id)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        follow = Follow.objects.filter(user=self.request.user)
        page = self.paginate_queryset(follow)
        serializer = SubscriptionsSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def get_serializer_context(self):
        if self.action in ('list',):
            return {
                'request': self.request
            }
        return {
            'user_id': self.kwargs['user_id'],
            'request': self.request
        }
