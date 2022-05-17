import pytest
import importlib
bg =  importlib.import_module('basket-game')


@pytest.fixture
def board1():
    sample_game = bg.Game()
    bg.board = bg.Board(sample_game)

# def test_
