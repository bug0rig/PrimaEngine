__all__ = ["GameWindow"]


def GameWindow(*args, **kwargs):
    from .game_client import GameWindow as _GW
    return _GW(*args, **kwargs)

