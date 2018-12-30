from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q  # helps construct queries
from django.urls import reverse


GAME_STATUS_CHOICES = (
    ('F', 'First Player To Move'),
    ('S', 'Second Player To Move'),
    ('W', 'First Player Wins'),
    ('L', 'Second Player Wins'),
    ('D', 'Draw')
)

BOARD_SIZE = 3


# going to help us retrieve data about games
class GamesQuerySet(models.QuerySet):
    def games_for_user(self, user):
        # returns if first player is user or second player is user
        return self.filter(
            Q(first_player=user) | Q(second_player=user)
        )

    def active(self):
        return self.filter(
            Q(status='F') | Q(status='S')
        )


class Game(models.Model):
    """Game data"""
    first_player = models.ForeignKey(User, related_name="games_first_player", on_delete=models.CASCADE)
    second_player = models.ForeignKey(User, related_name="games_second_player", on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, default='F', choices=GAME_STATUS_CHOICES)

    # lets us use the query set in the games class
    # overwriting objects with our custom one
    objects = GamesQuerySet.as_manager()

    def board(self):
        """Return a 2-dimensional list of Move objects,
        so you can ask for the state of a square at position [y][x]."""
        board = [[None for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        for move in self.move_set.all():
            board[move.y][move.x] = move
        return board

    def is_users_move(self, user):
        """Returns whether the it is the users turn depending if they are first or second player"""
        return (user == self.first_player and self.status == 'F') or\
               (user == self.second_player and self.status == 'S')

    def new_move(self):
        """Returns a new move object with player, game, and count present"""
        if self.status not in 'FS':
            raise ValueError("Cannot make move on finished game")

        return Move(
            game=self,
            by_first_player=self.status == 'F'
        )

    def update_after_move(self, move):
        """Update the status of the game, given the last move"""
        self.status = self._get_game_status_after_move(move)

    def _get_game_status_after_move(self, move):
        """Get the game status after a move takes place"""
        x, y = move.x, move.y
        board = self.board()
        if (board[y][0] == board[y][1] == board[y][2]) or \
            (board[0][x] == board[1][x] == board[2][x]) or \
            (board[0][0] == board[1][1] == board[2][2]) or \
                (board[0][2] == board[1][1] == board[2][0]):
            return "W" if move.by_first_player else "L"
        if self.move_set.count() >= BOARD_SIZE**2:
            return 'D'
        return 'S' if self.status == 'F' else 'F'

    # django will use this method to go to the correct url
    def get_absolute_url(self):
        """Constructs url from the mapping"""
        return reverse('gameplay_detail', args=[self.id])

    def __str__(self):
        return "{0} vs {1}".format(self.first_player, self.second_player)


class Move(models.Model):
    """Move data"""
    x = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(BOARD_SIZE-1)])
    y = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(BOARD_SIZE-1)])
    comment = models.CharField(max_length=300, blank=True)
    game = models.ForeignKey(Game, editable=False, on_delete=models.CASCADE)
    by_first_player = models.BooleanField(editable=False)

    def __eq__(self, other):
        """Check if move is by the same player"""
        if other is None:
            return False
        return other.by_first_player == self.by_first_player

    def save(self, *args, **kwargs):
        """first saves the move then saves the game status"""
        super(Move, self).save(*args, **kwargs)
        self.game.update_after_move(self)
        self.game.save()
