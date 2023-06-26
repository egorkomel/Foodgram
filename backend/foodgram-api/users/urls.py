from django.urls import include, path
from users.views import SubscriptionsViewSet

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionsViewSet.as_view({'get': 'list'})
    ),
    path('users/<int:user_id>/subscribe/', SubscriptionsViewSet.as_view({
        'post': 'create',
        'delete': 'destroy'
    })),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
