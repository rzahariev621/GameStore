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
from core.views import home, store, library, community, login, game_detail, register, logout_user, add_free_game, buy_game, add_review, add_to_wishlist, wishlist, remove_from_wishlist, profile
from django.conf import settings
from django.conf.urls.static import static

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

    path('game/<int:game_id>/add-free/', add_free_game, name='add_free_game'),
    path('game/<int:game_id>/buy/', buy_game, name='buy_game'),
    path('game/<int:game_id>/', game_detail, name='game_detail'),
    path('game/<int:game_id>/review/', add_review, name='add_review'),
    path('game/<int:game_id>/wishlist/', add_to_wishlist, name='add_to_wishlist'),
    path('game/<int:game_id>/wishlist/remove/', remove_from_wishlist, name='remove_from_wishlist'),
    
    path('profile/<str:username>/', profile, name='profile'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)