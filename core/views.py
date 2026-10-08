from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Q
from django.db import transaction

from .models import Game, Review, WishlistEntry, FriendRequest, VideoTutorial, TutorialPurchase, GameRequirement, Message, UserBlock, TutorialReport, CreatorPointTransaction, CreatorPointAccount

from .forms import VideoTutorialForm, GameForm, GameRequirementForm, AdminTutorialForm
import stripe

from decimal import Decimal 

def home(request):
    return render(request, 'core/home.html')

def store(request):
    games = Game.objects.all()
    return render(request, 'core/store.html', {'games': games})

@login_required
def library(request):
    purchases = TutorialPurchase.objects.filter(
        user=request.user
    ).select_related(
        'tutorial',
        'tutorial__game'
    ).order_by('-purchased_at')

    return render(
        request,
        'core/library.html',
        {
            'purchases': purchases
        }
    )

def community(request):
    users = User.objects.filter(
        is_active=True,
        is_staff=False
    ).order_by('username')

    recent_reviews = Review.objects.filter(
        status='approved'
    ).select_related(
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
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password != password_confirm:
            return render(
                request,
                'core/register.html',
                {
                    'error': 'Passwords are not matching.'
                }
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'core/register.html',
                {
                    'error': 'Username already exists.'
                }
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                'core/register.html',
                {
                    'error': 'Email is already in use.'
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        auth_login(request, user)

        return redirect('home')

    return render(
        request,
        'core/register.html'
    )

def logout_user(request):
    auth_logout(request)
    return redirect('home')

#GAME DETAILS

def game_detail(request, game_id):
    game = get_object_or_404(
        Game,
        id=game_id
    )

    reviews = Review.objects.filter(
        game=game,
        status='approved'
    ).order_by('-created_at')

    requirements = GameRequirement.objects.filter(
        game=game
    ).first()

    tutorials = VideoTutorial.objects.filter(
        game=game,
        status='approved'
    ).select_related(
        'publisher'
    ).order_by('-created_at')

    return render(
        request,
        'core/game_detail.html',
        {
            'game': game,
            'reviews': reviews,
            'requirements': requirements,
            'tutorials': tutorials,
        }
    )

@login_required
def add_review(request, game_id):
    game = get_object_or_404(
        Game,
        id=game_id
    )

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:

            Review.objects.update_or_create(
                user=request.user,
                game=game,
                defaults={
                    'rating': rating,
                    'comment': comment,
                    'status': 'pending'
                }
            )

    return redirect(
        'game_detail',
        game_id=game.id
    )

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

    reviews = Review.objects.filter(
        user=profile_user,
        status='approved'
    ).order_by('-created_at')

    published_tutorials = VideoTutorial.objects.filter(
        publisher=profile_user,
        status='approved'
    ).order_by('-created_at')

    role = 'User'

    if profile_user.groups.filter(name='Admin').exists():
        role = 'Admin'
    elif profile_user.groups.filter(name='Moderator').exists():
        role = 'Moderator'
    elif profile_user.groups.filter(name='Publisher').exists():
        role = 'Publisher'

    request_sent = False
    incoming_request = False
    is_friend = False

    is_blocked_by_me = False
    has_blocked_me = False

    if request.user.is_authenticated and request.user != profile_user:

        is_blocked_by_me = UserBlock.objects.filter(
            blocker=request.user,
            blocked=profile_user
        ).exists()

        has_blocked_me = UserBlock.objects.filter(
            blocker=profile_user,
            blocked=request.user
        ).exists()

        sent_request = FriendRequest.objects.filter(
            sender=request.user,
            receiver=profile_user
        ).first()

        received_request = FriendRequest.objects.filter(
            sender=profile_user,
            receiver=request.user
        ).first()

        if sent_request:
            if sent_request.status == 'pending':
                request_sent = True

            elif sent_request.status == 'accepted':
                is_friend = True

        if received_request:
            if received_request.status == 'pending':
                incoming_request = True

            elif received_request.status == 'accepted':
                is_friend = True

    return render(
        request,
        'core/profile.html',
        {
            'profile_user': profile_user,
            'reviews': reviews,
            'published_tutorials': published_tutorials,
            'role': role,
            'request_sent': request_sent,
            'incoming_request': incoming_request,
            'is_friend': is_friend,
            'is_blocked_by_me': is_blocked_by_me,
            'has_blocked_me': has_blocked_me,
        }
    )


@login_required
def send_friend_request(request, username):
    receiver = get_object_or_404(User, username=username)

    if request.method == 'POST':

        if (
            receiver != request.user
            and not users_are_blocked(request.user, receiver)
        ):

            already_exists = FriendRequest.objects.filter(
                sender=request.user,
                receiver=receiver
            ).exists()

            reverse_exists = FriendRequest.objects.filter(
                sender=receiver,
                receiver=request.user
            ).exists()

            if not already_exists and not reverse_exists:
                FriendRequest.objects.create(
                    sender=request.user,
                    receiver=receiver
                )

    return redirect(
        'profile',
        username=receiver.username
    )


@login_required
def accept_friend_request(request, username):
    sender = get_object_or_404(User, username=username)

    if users_are_blocked(request.user, sender):
        return redirect(
            'profile',
            username=sender.username
        )

    if request.method == 'POST':

        friend_request = FriendRequest.objects.filter(
            sender=sender,
            receiver=request.user,
            status='pending'
        ).first()

        if friend_request:
            friend_request.status = 'accepted'
            friend_request.save()

    return redirect(
        'profile',
        username=sender.username
    )

#PUBLISHER
@login_required
def publisher_dashboard(request):
    is_publisher = request.user.groups.filter(
        name='Publisher'
    ).exists()

    if not is_publisher:
        return redirect('home')

    tutorials = VideoTutorial.objects.filter(
        publisher=request.user
    ).order_by('-created_at')

    creator_account, created = CreatorPointAccount.objects.get_or_create(
        user=request.user
    )

    transactions = CreatorPointTransaction.objects.filter(
        user=request.user
    ).select_related(
        'tutorial'
    ).order_by('-created_at')

    return render(
        request,
        'core/publisher_dashboard.html',
        {
            'tutorials': tutorials,
            'creator_account': creator_account,
            'transactions': transactions,
        }
    )

#TUTORIAL UPLOAD
@login_required
def upload_tutorial(request):
    is_publisher = request.user.groups.filter(
        name='Publisher'
    ).exists()

    if not is_publisher:
        return redirect('home')

    if request.method == 'POST':

        form = VideoTutorialForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            tutorial = form.save(commit=False)

            tutorial.publisher = request.user
            tutorial.status = 'pending'

            tutorial.save()

            return redirect('publisher_dashboard')

    else:
        form = VideoTutorialForm()

    return render(
        request,
        'core/upload_tutorial.html',
        {
            'form': form
        }
    )

#TUTORAL DETAILS

def tutorial_detail(request, tutorial_id):
    tutorial = get_object_or_404(
        VideoTutorial.objects.select_related(
            'game',
            'publisher'
        ),
        id=tutorial_id,
        status='approved'
    )

    is_purchased = False
    is_owner = False
    is_publisher = False
    has_reported = False
    creator_balance = Decimal('0.00')
    can_afford_with_points = False

    if request.user.is_authenticated:

        is_owner = (
            request.user == tutorial.publisher
        )

        is_publisher = request.user.groups.filter(
            name='Publisher'
        ).exists()

        if tutorial.price > 0:
            is_purchased = TutorialPurchase.objects.filter(
                user=request.user,
                tutorial=tutorial
            ).exists()

        has_reported = TutorialReport.objects.filter(
            reporter=request.user,
            tutorial=tutorial
        ).exists()

        if is_publisher:
            creator_account, created = CreatorPointAccount.objects.get_or_create(
                user=request.user
            )

            creator_balance = creator_account.balance

            can_afford_with_points = (
                creator_balance >= tutorial.price
            )

    can_watch = (
        tutorial.price == 0
        or is_purchased
        or is_owner
    )

    return render(
        request,
        'core/tutorial_detail.html',
        {
            'tutorial': tutorial,
            'is_purchased': is_purchased,
            'is_owner': is_owner,
            'is_publisher': is_publisher,
            'can_watch': can_watch,
            'has_reported': has_reported,
            'creator_balance': creator_balance,
            'can_afford_with_points': can_afford_with_points,
        }
    )

#MODERATOR FUNCTIONS

@login_required
def moderator_dashboard(request):
    is_moderator = request.user.groups.filter(
        name='Moderator'
    ).exists()

    if not is_moderator:
        return redirect('home')

    pending_tutorials = VideoTutorial.objects.filter(
        status='pending'
    ).select_related(
        'game',
        'publisher'
    ).order_by('created_at')

    pending_reviews = Review.objects.filter(
        status='pending'
    ).select_related(
        'game',
        'user'
    ).order_by('created_at')

    pending_reports = TutorialReport.objects.filter(
        status='pending'
    ).select_related(
        'tutorial',
        'tutorial__game',
        'tutorial__publisher',
        'reporter'
    ).order_by('created_at')

    return render(
        request,
        'core/moderator_dashboard.html',
        {
            'pending_tutorials': pending_tutorials,
            'pending_reviews': pending_reviews,
            'pending_reports': pending_reports,
        }
    )


@login_required
def approve_tutorial(request, tutorial_id):
    is_moderator = request.user.groups.filter(
        name='Moderator'
    ).exists()

    if not is_moderator:
        return redirect('home')

    tutorial = get_object_or_404(
        VideoTutorial,
        id=tutorial_id,
        status='pending'
    )

    if request.method == 'POST':
        tutorial.status = 'approved'
        tutorial.save(update_fields=['status'])

    return redirect('moderator_dashboard')


@login_required
def reject_tutorial(request, tutorial_id):
    is_moderator = request.user.groups.filter(
        name='Moderator'
    ).exists()

    if not is_moderator:
        return redirect('home')

    tutorial = get_object_or_404(
        VideoTutorial,
        id=tutorial_id,
        status='pending'
    )

    if request.method == 'POST':
        tutorial.status = 'rejected'
        tutorial.save(update_fields=['status'])

    return redirect('moderator_dashboard')



@login_required
def approve_review(request, review_id):
    is_moderator = request.user.groups.filter(
        name='Moderator'
    ).exists()

    if not is_moderator:
        return redirect('home')

    review = get_object_or_404(
        Review,
        id=review_id,
        status='pending'
    )

    if request.method == 'POST':
        review.status = 'approved'
        review.save(update_fields=['status'])

    return redirect('moderator_dashboard')



@login_required
def reject_review(request, review_id):
    is_moderator = request.user.groups.filter(
        name='Moderator'
    ).exists()

    if not is_moderator:
        return redirect('home')

    review = get_object_or_404(
        Review,
        id=review_id,
        status='pending'
    )

    if request.method == 'POST':
        review.status = 'rejected'
        review.save(update_fields=['status'])

    return redirect('moderator_dashboard')






@login_required
def resolve_tutorial_report(request, report_id):
    is_moderator = request.user.groups.filter(
        name='Moderator'
    ).exists()

    if not is_moderator:
        return redirect('home')

    report = get_object_or_404(
        TutorialReport,
        id=report_id,
        status='pending'
    )

    if request.method == 'POST':
        report.status = 'resolved'
        report.save(
            update_fields=['status']
        )

    return redirect('moderator_dashboard')

#STRIPE FUNCTIONS

@login_required
def create_checkout_session(request, tutorial_id):
    tutorial = get_object_or_404(
        VideoTutorial,
        id=tutorial_id,
        status='approved'
    )

    # Free tutorial
    if tutorial.price == 0:
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    # Publisher cannot buy their own tutorial
    if tutorial.publisher == request.user:
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    # Publishers do not use Stripe
    is_publisher = request.user.groups.filter(
        name='Publisher'
    ).exists()

    if is_publisher:
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    # Already purchased
    already_purchased = TutorialPurchase.objects.filter(
        user=request.user,
        tutorial=tutorial
    ).exists()

    if already_purchased:
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        mode='payment',

        line_items=[
            {
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': tutorial.title,
                    },
                    'unit_amount': int(
                        tutorial.price * 100
                    ),
                },
                'quantity': 1,
            }
        ],

        success_url=request.build_absolute_uri(
            '/payment/success/'
        ),

        cancel_url=request.build_absolute_uri(
            f'/tutorial/{tutorial.id}/'
        ),

        metadata={
            'tutorial_id': str(tutorial.id),
            'user_id': str(request.user.id),
        }
    )

    return redirect(
        checkout_session.url,
        code=303
    )


@login_required
def payment_success(request):
    return render(
        request,
        'core/payment_success.html'
    )


#WEBHOOK

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    signature = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )

    except ValueError:
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)


    if event.type == 'checkout.session.completed':

        session = event.data.object

        if session.payment_status == 'paid':

            tutorial_id = session.metadata['tutorial_id']
            user_id = session.metadata['user_id']

            tutorial = VideoTutorial.objects.filter(
                id=tutorial_id,
                status='approved'
            ).first()

            user = User.objects.filter(
                id=user_id
            ).first()


            if tutorial and user:

                amount_total = session.amount_total or 0

                price_paid = (
                    Decimal(amount_total)
                    / Decimal('100')
                )


                purchase, created = TutorialPurchase.objects.get_or_create(
                    user=user,
                    tutorial=tutorial,
                    defaults={
                        'price_paid': price_paid
                    }
                )


                if created:

                    creator_account, account_created = (
                        CreatorPointAccount.objects.get_or_create(
                            user=tutorial.publisher
                        )
                    )

                    creator_account.balance += price_paid
                    creator_account.save(
                        update_fields=['balance']
                    )


                    CreatorPointTransaction.objects.create(
                        user=tutorial.publisher,
                        tutorial=tutorial,
                        amount=price_paid,
                        transaction_type='sale'
                    )


    return HttpResponse(status=200)


#ADMIN DASHBOARD
@login_required
def admin_dashboard(request):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    users_count = User.objects.count()
    games_count = Game.objects.count()
    tutorials_count = VideoTutorial.objects.count()
    reviews_count = Review.objects.count()

    return render(
        request,
        'core/admin_dashboard.html',
        {
            'users_count': users_count,
            'games_count': games_count,
            'tutorials_count': tutorials_count,
            'reviews_count': reviews_count,
        }
    )

#MANAGE USERS
@login_required
def manage_users(request):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    users = User.objects.all().order_by('username')

    for account in users:

        if account.is_superuser:
            account.current_role = 'Superuser'

        elif account.groups.filter(name='Admin').exists():
            account.current_role = 'Admin'

        elif account.groups.filter(name='Moderator').exists():
            account.current_role = 'Moderator'

        elif account.groups.filter(name='Publisher').exists():
            account.current_role = 'Publisher'

        else:
            account.current_role = 'User'

    return render(
        request,
        'core/manage_users.html',
        {
            'users': users
        }
    )


@login_required
def update_user_role(request, user_id):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    user_to_update = get_object_or_404(
        User,
        id=user_id
    )

    if request.method == 'POST':

        role = request.POST.get('role')

        # Не позволяваме промяна на superuser
        if user_to_update.is_superuser:
            return redirect('manage_users')

        # Не позволяваме администраторът да си смени
        # собствената роля и да загуби достъп
        if user_to_update == request.user:
            return redirect('manage_users')

        special_groups = Group.objects.filter(
            name__in=[
                'Publisher',
                'Moderator',
                'Admin'
            ]
        )

        user_to_update.groups.remove(
            *special_groups
        )

        if role in [
            'Publisher',
            'Moderator',
            'Admin'
        ]:
            group = Group.objects.get(
                name=role
            )

            user_to_update.groups.add(
                group
            )

    return redirect('manage_users')


@login_required
def toggle_user_active(request, user_id):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    account = get_object_or_404(
        User,
        id=user_id
    )

    if request.method == 'POST':

        # Не позволяваме да се блокира superuser
        if account.is_superuser:
            return redirect('manage_users')

        # Не позволяваме администраторът да блокира себе си
        if account == request.user:
            return redirect('manage_users')

        account.is_active = not account.is_active
        account.save(
            update_fields=['is_active']
        )

    return redirect('manage_users')

#MANAGE GAMES
@login_required
def manage_games(request):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    games = Game.objects.all().order_by('title')

    return render(
        request,
        'core/manage_games.html',
        {
            'games': games
        }
    )


@login_required
def add_game(request):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    if request.method == 'POST':

        game_form = GameForm(
            request.POST,
            request.FILES
        )

        requirements_form = GameRequirementForm(
            request.POST
        )

        if game_form.is_valid() and requirements_form.is_valid():

            game = game_form.save()

            requirements = requirements_form.save(
                commit=False
            )

            requirements.game = game
            requirements.save()

            return redirect('manage_games')

    else:
        game_form = GameForm()
        requirements_form = GameRequirementForm()

    return render(
        request,
        'core/add_game.html',
        {
            'game_form': game_form,
            'requirements_form': requirements_form,
        }
    )



@login_required
def edit_game(request, game_id):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    game = get_object_or_404(
        Game,
        id=game_id
    )

    requirements = GameRequirement.objects.filter(
        game=game
    ).first()

    if request.method == 'POST':

        game_form = GameForm(
            request.POST,
            request.FILES,
            instance=game
        )

        requirements_form = GameRequirementForm(
            request.POST,
            instance=requirements
        )

        if game_form.is_valid() and requirements_form.is_valid():

            game = game_form.save()

            requirements = requirements_form.save(
                commit=False
            )

            requirements.game = game
            requirements.save()

            return redirect('manage_games')

    else:

        game_form = GameForm(
            instance=game
        )

        requirements_form = GameRequirementForm(
            instance=requirements
        )

    return render(
        request,
        'core/edit_game.html',
        {
            'game': game,
            'game_form': game_form,
            'requirements_form': requirements_form,
        }
    )



@login_required
def delete_game(request, game_id):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    game = get_object_or_404(
        Game,
        id=game_id
    )

    if request.method == 'POST':
        game.delete()

        return redirect('manage_games')

    return render(
        request,
        'core/delete_game.html',
        {
            'game': game
        }
    )

#MANAGE TUTORIALS

@login_required
def manage_tutorials(request):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    tutorials = VideoTutorial.objects.select_related(
        'game',
        'publisher'
    ).order_by('-created_at')

    return render(
        request,
        'core/manage_tutorials.html',
        {
            'tutorials': tutorials
        }
    )



@login_required
def edit_tutorial(request, tutorial_id):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    tutorial = get_object_or_404(
        VideoTutorial,
        id=tutorial_id
    )

    if request.method == 'POST':

        form = AdminTutorialForm(
            request.POST,
            request.FILES,
            instance=tutorial
        )

        if form.is_valid():
            form.save()

            return redirect('manage_tutorials')

    else:

        form = AdminTutorialForm(
            instance=tutorial
        )

    return render(
        request,
        'core/edit_tutorial.html',
        {
            'tutorial': tutorial,
            'form': form,
        }
    )



@login_required
def delete_tutorial(request, tutorial_id):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    tutorial = get_object_or_404(
        VideoTutorial,
        id=tutorial_id
    )

    if request.method == 'POST':
        tutorial.delete()

        return redirect('manage_tutorials')

    return render(
        request,
        'core/delete_tutorial.html',
        {
            'tutorial': tutorial
        }
    )


#MANAGE REVIEWS
@login_required
def manage_reviews(request):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    reviews = Review.objects.select_related(
        'user',
        'game'
    ).order_by('-created_at')

    return render(
        request,
        'core/manage_reviews.html',
        {
            'reviews': reviews
        }
    )


@login_required
def update_review_status(request, review_id):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    review = get_object_or_404(
        Review,
        id=review_id
    )

    if request.method == 'POST':

        status = request.POST.get('status')

        if status in [
            'pending',
            'approved',
            'rejected'
        ]:
            review.status = status
            review.save(
                update_fields=['status']
            )

    return redirect('manage_reviews')

@login_required
def delete_review(request, review_id):
    is_admin = (
        request.user.is_superuser
        or request.user.groups.filter(name='Admin').exists()
    )

    if not is_admin:
        return redirect('home')

    review = get_object_or_404(
        Review,
        id=review_id
    )

    if request.method == 'POST':
        review.delete()

        return redirect('manage_reviews')

    return render(
        request,
        'core/delete_review.html',
        {
            'review': review
        }
    )


#CHAT

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(
        User,
        username=username
    )

    if other_user == request.user:
        return redirect(
            'profile',
            username=request.user.username
        )

    if users_are_blocked(request.user, other_user):
        return redirect(
            'profile',
            username=other_user.username
        )

    if not users_are_friends(request.user, other_user):
        return redirect(
            'profile',
            username=other_user.username
        )

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()

        if text:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                text=text
            )

        return redirect(
            'chat',
            username=other_user.username
        )

    conversation = Message.objects.filter(
        Q(
            sender=request.user,
            receiver=other_user
        ) |
        Q(
            sender=other_user,
            receiver=request.user
        )
    ).select_related(
        'sender',
        'receiver'
    ).order_by('created_at')

    return render(
        request,
        'core/chat.html',
        {
            'other_user': other_user,
            'conversation': conversation
        }
    )



@login_required
def messages_inbox(request):
    messages = Message.objects.filter(
        Q(sender=request.user)
        |
        Q(receiver=request.user)
    ).select_related(
        'sender',
        'receiver'
    ).order_by('-created_at')

    conversations = []
    seen_users = set()

    for message in messages:

        if message.sender == request.user:
            other_user = message.receiver
        else:
            other_user = message.sender

        if users_are_blocked(request.user, other_user):
            continue

        if other_user.id not in seen_users:

            conversations.append(
                {
                    'user': other_user,
                    'last_message': message,
                }
            )

            seen_users.add(other_user.id)

    return render(
        request,
        'core/messages_inbox.html',
        {
            'conversations': conversations
        }
    )

#USER BLOCK

def users_are_blocked(user1, user2):
    return UserBlock.objects.filter(
        Q(blocker=user1, blocked=user2) |
        Q(blocker=user2, blocked=user1)
    ).exists()


def users_are_friends(user1, user2):
    return FriendRequest.objects.filter(
        Q(
            sender=user1,
            receiver=user2,
            status='accepted'
        ) |
        Q(
            sender=user2,
            receiver=user1,
            status='accepted'
        )
    ).exists()

@login_required
def block_user(request, username):
    user_to_block = get_object_or_404(User, username=username)

    if user_to_block == request.user:
        return redirect('profile', username=username)

    if request.method == 'POST':
        UserBlock.objects.get_or_create(
            blocker=request.user,
            blocked=user_to_block
        )

        FriendRequest.objects.filter(
            Q(sender=request.user, receiver=user_to_block) |
            Q(sender=user_to_block, receiver=request.user)
        ).delete()

    return redirect('profile', username=username)


@login_required
def unblock_user(request, username):
    user_to_unblock = get_object_or_404(User, username=username)

    if request.method == 'POST':
        UserBlock.objects.filter(
            blocker=request.user,
            blocked=user_to_unblock
        ).delete()

    return redirect('profile', username=username)


@login_required
def blocked_users(request):
    blocks = UserBlock.objects.filter(
        blocker=request.user
    ).select_related(
        'blocked'
    ).order_by('-created_at')

    return render(
        request,
        'core/blocked_users.html',
        {
            'blocks': blocks
        }
    )

#REPORTING

@login_required
def report_tutorial(request, tutorial_id):
    tutorial = get_object_or_404(
        VideoTutorial,
        id=tutorial_id,
        status='approved'
    )

    if request.user == tutorial.publisher:
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()

        if reason:
            TutorialReport.objects.get_or_create(
                reporter=request.user,
                tutorial=tutorial,
                defaults={
                    'reason': reason
                }
            )

    return redirect(
        'tutorial_detail',
        tutorial_id=tutorial.id
    )


#CREATOR POINTS

@login_required
def buy_with_creator_points(request, tutorial_id):
    tutorial = get_object_or_404(
        VideoTutorial,
        id=tutorial_id,
        status='approved'
    )

    is_publisher = request.user.groups.filter(
        name='Publisher'
    ).exists()

    if not is_publisher:
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    if tutorial.publisher == request.user:
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    if tutorial.price == 0:
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    if request.method != 'POST':
        return redirect(
            'tutorial_detail',
            tutorial_id=tutorial.id
        )

    with transaction.atomic():

        CreatorPointAccount.objects.get_or_create(
            user=request.user
        )

        CreatorPointAccount.objects.get_or_create(
            user=tutorial.publisher
        )

        buyer_account = CreatorPointAccount.objects.select_for_update().get(
            user=request.user
        )

        seller_account = CreatorPointAccount.objects.select_for_update().get(
            user=tutorial.publisher
        )

        already_purchased = TutorialPurchase.objects.filter(
            user=request.user,
            tutorial=tutorial
        ).exists()

        if already_purchased:
            return redirect(
                'tutorial_detail',
                tutorial_id=tutorial.id
            )

        if buyer_account.balance < tutorial.price:
            return redirect(
                'tutorial_detail',
                tutorial_id=tutorial.id
            )

        buyer_account.balance -= tutorial.price
        seller_account.balance += tutorial.price

        buyer_account.save(
            update_fields=['balance']
        )

        seller_account.save(
            update_fields=['balance']
        )

        TutorialPurchase.objects.create(
            user=request.user,
            tutorial=tutorial,
            price_paid=tutorial.price
        )

        CreatorPointTransaction.objects.create(
            user=request.user,
            tutorial=tutorial,
            amount=tutorial.price,
            transaction_type='purchase'
        )

        CreatorPointTransaction.objects.create(
            user=tutorial.publisher,
            tutorial=tutorial,
            amount=tutorial.price,
            transaction_type='sale'
        )

    return redirect(
        'tutorial_detail',
        tutorial_id=tutorial.id
    )