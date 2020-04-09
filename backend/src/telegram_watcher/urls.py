from django.urls import path, include
from django.conf import settings
import telegram_watcher.views as views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    path(r'stripe_checkout/', views.StripeCheckoutView.as_view()),
    path(r'stripe_hook/', views.StripeEventView.as_view()),
    path(r'stripe_description/', views.StripeDescriptionView.as_view()),
    path(r'registration/', views.RegistrationView.as_view()),
    path(r'check_email/', views.CheckEmailView.as_view()),
    path(r'auth/', obtain_jwt_token),
    path(r'auth/refresh/', refresh_jwt_token),
    path(r'message/<int:pk>/', views.MessageDetail.as_view()),
    path(r'message/count/', views.MessageCount.as_view()),
    path(r'user/', views.ProfileDetail.as_view()),
    path(r'feed/', views.FeedList.as_view()),
    path(r'feed/<int:pk>/', views.FeedDetail.as_view()),
    path(r'source/', views.SourceList.as_view()),
    path(r'source_group/', views.SourceGroupList.as_view()),
    path(r'source/<int:pk>/', views.SourceDetail.as_view()),
    path(r'feed_message/favorites/', views.FavoritesMessageList.as_view()),
    path(r'feed_message/favorites/<int:pk>/', views.AddMessageToFavorites.as_view()),
    path(r'feed_message/favorites/<int:pk>/remove', views.RemoveMessageFromFavorites.as_view()),
    path(r'feed_message/failover/', views.FailOverMessageList.as_view()),
    path(r'feed_message/all/', views.MessageList.as_view()),
    path(r'feed_message/blacklist/<int:pk>/', views.AddAuthorToBlacklist.as_view()),
    path(r'feed_message/blacklist/<int:pk>/remove', views.RemoveAuthorFromBlacklist.as_view()),
    path(r'feed_message/<int:feed>/', views.FeedMessageList.as_view()),

    path(r'message/<int:pk>/share/',
         views.ShareMessageActionView.as_view()),
    path(r'shared/<int:pk>/',
         views.SharedMessageView.as_view()),
]

