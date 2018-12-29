from django.shortcuts import render, redirect


def welcome(request):
    """
    Display hello world
    """
    if request.user.is_authenticated:
        # name of the url we want to redirect to
        return redirect('player_home')
    else:
        return render(request, 'tictactoe/welcome.html')
