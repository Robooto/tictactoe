from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from gameplay.models import Game
from django.contrib.auth.decorators import login_required

from player.forms import InvitationForm
from .models import Invitation


@login_required()
def home(request):
    my_games = Game.objects.games_for_user(request.user)
    active_games = my_games.active()
    finished_games = my_games.difference(active_games)
    invitations = request.user.invitations_received.all()
    return render(request, "player/home.html", {'games': active_games,
                                                'finished_games': finished_games,
                                                'invitations': invitations})


@login_required()
def new_invitation(request):
    if request.method == "POST":
        # use form to check the data
        invitation = Invitation(from_user=request.user)
        form = InvitationForm(instance=invitation, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('player_home')
    else:
        form = InvitationForm()
    return render(request, "player/new_invitation_form.html", {'form': form})


@login_required()
def accept_invitation(request, id):
    invitation = get_object_or_404(Invitation, pk=id)
    if not request.user == invitation.to_user:
        raise PermissionDenied
    if request.method == 'POST':
        if "accept" in request.POST:
            game = Game.objects.create(first_player=invitation.to_user, second_player=invitation.from_user, )
        invitation.delete()
        # can redirect directly to game because of the url mapping that is happening on the model
        return redirect(game)
    else:
        return render(request, "player/accept_invitation_form.html", {'invitation': invitation})


class SignUpView(CreateView):  # create sign up view using the genreric create form class
    form_class = UserCreationForm
    template_name = "player/signup_form.html"
    success_url = reverse_lazy('player_home')
