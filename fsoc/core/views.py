from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
#from django.contrib.messages.views import SuccesMessageMixin
from django.views import View
from .form import RegisterForm, LoginForm, UpdateProfileForm, UpdateUserForm
from django.contrib.auth.decorators import login_required
from .models import friend


def home(request):
    return render(request, 'home.html')


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def friends(request):
    users_friends1 = friend.object.filter(user = request.user, confirmed = True)
    users_friends2 = friend.objects.filter(users_friend = request.user, confirmed = True)
    new_friends = friend.objects.filter(users_friend = request.user, confirmed = False).count()
    context = {"friends1": user_friends1, "friends2": users_friends, "not_confirmed_friends_count": new_friends}
    return render(request, 'friends.html', context)


@login_required
def friend_request(request):
    not_confirmed_friends = friend.object.filter(users_friend = request.user, confirmed = False)
    new_friends = friend.object.filter(users_friend = request.user, confirmed = False).count()
    context = {"not_confirmed_friends": not_confirmed_friends, "not_confirmed_friends_count": new_friends}
    return render(request, 'friend_request.html', context)


@login_required
def add_friend(request, account_id):
    try:
        user = User.objects.get(id = account_id)
    except:
        raise Http404("User no found")
    is_friend = friend.objects.filter(user = request.user, user_friend = user)
    if not is_friend:
        add_friend = friend(user=request.user, user_friend = user)
        add_friend.save()
    return HttpResponseRedirect(reverse('account:account', args = (account_id, )))


@login_required
def confirm_friend(request, account_id):
    try:
        user = User.objects.get(id = account_id)
    except:
        raise Http404('User not found')

    new_friend = friend.objects.get(user = user, users_friend = request.user)
    new_friend.confirmed = True
    new_friend.save()
    return HttpResponseRedirect(reverse('account:friends'))

@login_required

def delete_friend(request, account_id):
    try:
        user = User.objects.get(id = account_id)
    except:
        raise Http404("User no found")

    new_friend = friend.objects.filter(user = user, user_friend = request.user)|friend.objects.filter(
        user = request.user, users_friend = user)
    new_friend.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def find_users(request):
    if request.method == 'POST':
        user_setting = request.user
        search = request.POST.get('search')
        queryset = User.objects.all().exclude(username = request.user)
        if search:
            search_list = search.split(' ')
            if len(search_list) == 2:
                users = queryset.filter(Q(first_name__iexact=search_list[0]) &
                                        Q(last_name__iexact=search_list[1]))|Q(first_name__iexact=search_list[1])&Q(last_name__iexact=search_list[0])
            elif len(search_list) == 1:
                users = queryset.filter(Q(first_name__iexact=search_list[0])|Q(last_name__iexact=search_list[0]))
            else:
                users = False
        else:
            users = False
    else:
        users = User.object.all().exclude(username = request.user).order_by("-id")[:20]
    new_friends = friend.object.filter(user_friend = request.user, confirmed = False).count()
    context = {
        'users': users,
        "not_confirmed_friends_count": new_friends
    }
    return render(request,'users.html', context)

