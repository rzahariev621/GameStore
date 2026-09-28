from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Game, LibraryEntry, Purchase, Review, WishlistEntry

def home(request):
    return render(request, 'core/home.html')

def store(request):
    games = Game.objects.all()
    return render(request, 'core/store.html', {'games': games})

@login_required
def library(request):
    library_entries = LibraryEntry.objects.filter(user=request.user)

    return render(request,'core/library.html',{'library_entries': library_entries})

def community(request):
    users = User.objects.filter(
        is_active=True,
        is_staff=False
    ).order_by('username')

    recent_reviews = Review.objects.select_related(
        'user',
        'game'
    ).order_by('-created_at')[:10]

    return render(
        request,
        'core/community.html',
        {
            'users': users,
            'recent_reviews': recent_reviews
        }
    )
#LOGIN, REGISTER, LOGOUT

def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username = username, password = password)

        if user is not None:
            auth_login(request, user)

            return redirect('home')

        else:
            return render(request, 'core/login.html', {'error': 'Wrong username or password.'})


    return render(request, 'core/login.html')

def register(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password != password_confirm:
            return render(request,'core/register.html', {'error': 'Passwords are not matching.'})

        if User.objects.filter(username=username).exists():
            return render(request,'core/register.html', {'error': 'Username already exists.'})

        user = User.objects.create_user(
            username=username,
            password=password
        )

        auth_login(request, user)

        return redirect('home')

    return render(request, 'core/register.html')

def logout_user(request):
    auth_logout(request)
    return redirect('home')

#GAME DETAILS

def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    reviews = Review.objects.filter(
        game=game
    ).order_by('-created_at')

    is_owned = False

    if request.user.is_authenticated:
        is_owned = LibraryEntry.objects.filter(
            user=request.user,
            game=game
        ).exists()

    return render(
        request,
        'core/game_detail.html',
        {
            'game': game,
            'reviews': reviews,
            'is_owned': is_owned
        }
    )

@login_required
def add_review(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    owns_game = LibraryEntry.objects.filter(
        user=request.user,
        game=game
    ).exists()

    if not owns_game:
        return redirect('game_detail', game_id=game.id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            Review.objects.update_or_create(
                user=request.user,
                game=game,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )

    return redirect('game_detail', game_id=game.id)

@login_required
def add_free_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if game.price == 0:
        LibraryEntry.objects.get_or_create(
            user=request.user,
            game=game
        )

        WishlistEntry.objects.filter(
            user=request.user,
            game=game
        ).delete()

    return redirect('game_detail', game_id=game.id)

@login_required
def buy_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST' and game.price > 0:

        Purchase.objects.get_or_create(
            user=request.user,
            game=game,
            defaults={'price_paid': game.price}
        )

        LibraryEntry.objects.get_or_create(
            user=request.user,
            game=game
        )

        WishlistEntry.objects.filter(
            user=request.user,
            game=game
        ).delete()

    return redirect('game_detail', game_id=game.id)

#WISHLIST

@login_required
def add_to_wishlist(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        WishlistEntry.objects.get_or_create(user=request.user,game=game)

    return redirect('game_detail', game_id=game.id)

@login_required
def wishlist(request):
    wishlist_entries = WishlistEntry.objects.filter(user=request.user)

    return render(request,'core/wishlist.html',{'wishlist_entries': wishlist_entries})

@login_required
def remove_from_wishlist(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        WishlistEntry.objects.filter(
            user=request.user,
            game=game
        ).delete()

    return redirect('wishlist')

#USER PROFILE

def profile(request, username):
    profile_user = get_object_or_404(
        User,
        username=username
    )

    library_entries = LibraryEntry.objects.filter(
        user=profile_user
    )

    reviews = Review.objects.filter(
        user=profile_user
    ).order_by('-created_at')

    return render(
        request,
        'core/profile.html',
        {
            'profile_user': profile_user,
            'library_entries': library_entries,
            'reviews': reviews
        }
    )