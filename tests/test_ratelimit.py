import pytest

from discord_ai_bot.ratelimit import RateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_allows_up_to_capacity_then_blocks():
    clock = FakeClock()
    rl = RateLimiter(capacity=3, refill_rate=1.0, clock=clock)
    assert [rl.allow("u") for _ in range(3)] == [True, True, True]
    assert rl.allow("u") is False


def test_refills_over_time():
    clock = FakeClock()
    rl = RateLimiter(capacity=2, refill_rate=1.0, clock=clock)
    assert rl.allow("u") and rl.allow("u")
    assert rl.allow("u") is False
    clock.advance(1.0)  # one token back
    assert rl.allow("u") is True
    assert rl.allow("u") is False


def test_refill_caps_at_capacity():
    clock = FakeClock()
    rl = RateLimiter(capacity=2, refill_rate=5.0, clock=clock)
    rl.allow("u")
    clock.advance(100.0)
    assert rl.tokens_available("u") == 2.0


def test_keys_are_independent():
    clock = FakeClock()
    rl = RateLimiter(capacity=1, refill_rate=1.0, clock=clock)
    assert rl.allow("a") is True
    assert rl.allow("a") is False
    assert rl.allow("b") is True


def test_rejected_calls_do_not_consume_tokens():
    clock = FakeClock()
    rl = RateLimiter(capacity=1, refill_rate=1.0, clock=clock)
    rl.allow("u")
    assert rl.allow("u") is False
    assert rl.tokens_available("u") == 0.0


def test_reset_specific_and_all():
    clock = FakeClock()
    rl = RateLimiter(capacity=1, refill_rate=1.0, clock=clock)
    rl.allow("u")
    rl.reset("u")
    assert rl.allow("u") is True
    rl.allow("u")
    rl.reset()
    assert rl.allow("u") is True


def test_invalid_params_rejected():
    with pytest.raises(ValueError, match="capacity"):
        RateLimiter(capacity=0, refill_rate=1.0)
    with pytest.raises(ValueError, match="refill_rate"):
        RateLimiter(capacity=1, refill_rate=0)
