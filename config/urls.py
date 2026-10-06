"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from core.views import (
    home,
    store,
    library,
    community,
    login,
    register,
    logout_user,
    wishlist,
    publisher_dashboard,
    upload_tutorial,
    moderator_dashboard,
    approve_tutorial,
    reject_tutorial,
    approve_review,
    reject_review,
    tutorial_detail,
    create_checkout_session,
    stripe_webhook,
    payment_success,
    game_detail,
    add_review,
    add_to_wishlist,
    remove_from_wishlist,
    profile,
    send_friend_request,
    accept_friend_request,
    admin_dashboard,
    manage_users,
    update_user_role,
    toggle_user_active,
    manage_games,
    add_game,
    edit_game,
    delete_game,
    manage_tutorials,
    edit_tutorial,
    delete_tutorial,
    manage_reviews,
    update_review_status,
    delete_review,
    chat_view,
    messages_inbox,

)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('store/', store, name='store'),
    path('library/', library, name='library'),
    path('community/', community, name='community'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('wishlist/', wishlist, name='wishlist'),
    path('publisher/', publisher_dashboard, name='publisher_dashboard'),
    path('publisher/upload/', upload_tutorial, name='upload_tutorial'),
    path('moderator/', moderator_dashboard, name='moderator_dashboard'),
    path('moderator/tutorial/<int:tutorial_id>/approve/', approve_tutorial, name='approve_tutorial'),
    path('moderator/tutorial/<int:tutorial_id>/reject/', reject_tutorial, name='reject_tutorial'),
    path('moderator/review/<int:review_id>/approve/', approve_review, name='approve_review'),
    path('moderator/review/<int:review_id>/reject/', reject_review, name='reject_review'),
    path('tutorial/<int:tutorial_id>/', tutorial_detail, name='tutorial_detail'),
    path('tutorial/<int:tutorial_id>/checkout/', create_checkout_session, name='create_checkout_session'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    path('payment/success/', payment_success, name='payment_success'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset.html',
        email_template_name='core/password_reset_email.html',
        subject_template_name='core/password_reset_subject.txt'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'),name='password_reset_complete'),

    path('game/<int:game_id>/', game_detail, name='game_detail'),
    path('game/<int:game_id>/review/', add_review, name='add_review'),
    path('game/<int:game_id>/wishlist/', add_to_wishlist, name='add_to_wishlist'),
    path('game/<int:game_id>/wishlist/remove/', remove_from_wishlist, name='remove_from_wishlist'),
    
    path('profile/<str:username>/', profile, name='profile'),
    path('profile/<str:username>/add-friend/', send_friend_request, name='send_friend_request'),
    path('profile/<str:username>/accept-friend/', accept_friend_request, name='accept_friend_request'),

    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/',manage_users,name='manage_users'),
    path('admin-panel/users/<int:user_id>/role/',update_user_role,name='update_user_role'),
    path('admin-panel/users/<int:user_id>/active/', toggle_user_active, name='toggle_user_active'),
    path('admin-panel/games/', manage_games,name='manage_games'),
    path('admin-panel/games/add/', add_game,name='add_game'),
    path('admin-panel/games/<int:game_id>/edit/' ,edit_game, name='edit_game'),
    path('admin-panel/games/<int:game_id>/delete/', delete_game, name='delete_game'),
    path('admin-panel/tutorials/', manage_tutorials, name='manage_tutorials'),
    path('admin-panel/tutorials/<int:tutorial_id>/edit/', edit_tutorial, name='edit_tutorial'),
    path('admin-panel/tutorials/<int:tutorial_id>/delete/', delete_tutorial, name='delete_tutorial'),
    path('admin-panel/reviews/', manage_reviews, name='manage_reviews'),
    path('admin-panel/reviews/<int:review_id>/status/', update_review_status, name='update_review_status'),
    path('admin-panel/reviews/<int:review_id>/delete/', delete_review, name='delete_review'),

    path('messages/<str:username>/', chat_view, name='chat'),
    path('messages/',messages_inbox,name='messages_inbox'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)