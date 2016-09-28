from modules.delays import Delay
from modules.gui import TextLabel
from internal_events import InternalEvent


LABEL_COLOR = (255, 255, 255)
HIGHSCORE_LABEL_CAPTION = "score: {score}"
HIGHSCORE_LABEL_X = 64
HIGHSCORE_LABEL_Y = 64
TIME_LABEL_CAPTION = "elapsed: {seconds}s"
TIME_LABEL_X = 64
TIME_LABEL_Y = 100

app_ = None
highscore_label = None
time_label = None

highscore = 0
time_ = 0
time_delay = None


def update_time():
    global time_, time_delay
    time_ += 1

    time_label.caption = TIME_LABEL_CAPTION.format(seconds=time_)
    time_label.render()

    time_delay = Delay(1, update_time)


@InternalEvent('load')
def on_load(app):
    global app_, highscore_label, time_label
    app_ = app

    highscore_label = TextLabel(
        HIGHSCORE_LABEL_X, HIGHSCORE_LABEL_Y,
        HIGHSCORE_LABEL_CAPTION.format(score=0), 48, LABEL_COLOR,
        caption_bold=True)

    highscore_label.render()

    time_label = TextLabel(
        TIME_LABEL_X, TIME_LABEL_Y, TIME_LABEL_CAPTION.format(seconds=0),
        32, LABEL_COLOR)

    time_label.render()

    app_.register_drawer('score', highscore_label.draw)
    app_.register_drawer('score', time_label.draw)


@InternalEvent('fruit_eaten')
def on_game_start(fruit):
    global highscore
    highscore += 1

    highscore_label.caption = HIGHSCORE_LABEL_CAPTION.format(score=highscore)
    highscore_label.render()


@InternalEvent('game_start')
def on_game_end():
    global highscore, time_, time_delay
    highscore = 0
    time_ = -1

    highscore_label.caption = HIGHSCORE_LABEL_CAPTION.format(score=highscore)
    highscore_label.render()

    update_time()


@InternalEvent('game_end')
def on_game_end():
    time_delay.cancel()
