from pytest import fixture
from typing import Any
import pytest

import hydra_once


@fixture(
    params=[
        # hydra._internal.instantiate._instantiate2.instantiate,
        hydra_once.instantiate
    ],
    ids=[
        "instantiate_once",
    ],
)
def instantiate_func(request: Any) -> Any:
    return request.param

cache = {}

def test_instantiated_once_standard(
    instantiate_func: Any,
) -> None:
    # standard behavior calls target every time
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "counter_key": "standard_behavior",
    }
    assert instantiate_func(cfg, cache=cache) == (1, "standard_behavior")
    assert instantiate_func(cfg, cache=cache) == (2, "standard_behavior")


def test_instantiated_once_keyword(
    instantiate_func: Any,
) -> None:
    # once behavior calls target only once
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "counter_key": "singleton_once_true",
    }

    assert instantiate_func(cfg, cache=cache) == (1, "singleton_once_true")
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_once_true")


def test_instantiated_once_manual_key1(
    instantiate_func: Any,
) -> None:
    # With manual key, gives same value, even if config changes.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": "manual_key1",
        "counter_key": "singleton_manual_key",
    }
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_manual_key")
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_manual_key")

    cfg["counter_key"] = "singleton_manual_key_changed"
    cfg["disallowed_arg"] = "broken"
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_manual_key")
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_manual_key")


def test_instantiated_once_auto_key(
    instantiate_func: Any,
) -> None:
    # With auto key, change to the config makes new call.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "counter_key": "singleton_auto_key",
    }
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_auto_key")
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_auto_key")

    cfg["counter_key"] = "singleton_auto_key_changed"
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_auto_key_changed")
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_auto_key_changed")


def test_instantiated_once_partial_change(
    instantiate_func: Any,
) -> None:
    # Changing _partial_ makes new signature for auto key.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "counter_key": "singleton_partial_change",
    }
    instance = instantiate_func(cfg, cache=cache)
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_partial_change")

    # setting as default does nothing
    # this behavior can be removed in the future if code base changes.
    cfg["_partial_"] = False
    assert instantiate_func(cfg, cache=cache) is instance

    # changing busts the key
    cfg["_partial_"] = True
    assert instantiate_func(cfg, cache=cache) is not instance

    instance = instantiate_func(cfg, cache=cache)
    assert instance() == (2, "singleton_partial_change")  # return is being called now!
    assert instance() == (3, "singleton_partial_change")


def test_instantiated_once_recursive_change(
    instantiate_func: Any,
) -> None:
    # Changing _recursive_ makes new signature for auto key.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "counter_key": "singleton_recursive_change",
    }
    instance = instantiate_func(cfg, cache=cache)
    assert instance is instantiate_func(cfg, cache=cache)

    # setting as default does nothing
    # this behavior can be removed in the future if code base changes.
    cfg["_recursive_"] = True
    assert instance is instantiate_func(cfg, cache=cache)

    # changing busts the key
    cfg["_recursive_"] = False
    assert instance is not instantiate_func(cfg, cache=cache)


def test_instantiated_once_convert_change(
    instantiate_func: Any,
) -> None:
    # Changing _convert_ makes new signature for auto key.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "counter_key": "singleton_convert_change",
    }
    instance = instantiate_func(cfg, cache=cache)
    assert instance is instantiate_func(cfg, cache=cache)

    # setting as default still busts cache
    cfg["_convert_"] = "null"
    assert instance is not instantiate_func(cfg, cache=cache)

    # changing busts the key
    cfg["_convert_"] = "partial"
    assert instance is not instantiate_func(cfg, cache=cache)


def test_instantiated_once_target_change(
    instantiate_func: Any,
) -> None:
    # Changing _target_ makes new signature for auto key.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "counter_key": "singleton_target_change",
    }
    assert instantiate_func(cfg, cache=cache) == (1, "singleton_target_change")

    cfg["_target_"] = "tests.instantiate.counter_function2"
    assert instantiate_func(cfg, cache=cache) == (2, "singleton_target_change", "counter_function2")
    assert instantiate_func(cfg, cache=cache) == (2, "singleton_target_change", "counter_function2")


def test_instantiated_once_nested(
    instantiate_func: Any,
) -> None:
    # Nested config with singleton base
    cfg = {
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "counter_key": "singleton_nested_base",
        },
        "ref1": "${base}",
        "ref2": "${base}",
    }
    x = instantiate_func(cfg, cache=cache)
    assert x.base == (1, "singleton_nested_base")
    assert x.ref1 == (1, "singleton_nested_base")
    assert x.ref2 == (1, "singleton_nested_base")

    x = instantiate_func(cfg, cache=cache)
    assert x.base == (1, "singleton_nested_base")
    assert x.ref1 == (1, "singleton_nested_base")
    assert x.ref2 == (1, "singleton_nested_base")


def test_instantiated_once_custom_cache(
    instantiate_func: Any,
) -> None:
    # Custom cache with singleton base
    cfg = {
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "counter_key": "singleton_custom_cache",
        },
        "ref1": "${base}",
        "ref2": "${base}",
    }

    # you can specify a custom cache too.

    x = instantiate_func(cfg, cache=cache)
    assert x.base == (1, "singleton_custom_cache")
    assert x.ref1 == (1, "singleton_custom_cache")
    assert x.ref2 == (1, "singleton_custom_cache")

    x = instantiate_func(cfg, cache=cache)
    assert x.base == (1, "singleton_custom_cache")
    assert x.ref1 == (1, "singleton_custom_cache")
    assert x.ref2 == (1, "singleton_custom_cache")


def test_instantiated_once_ephemeral_cache(
    instantiate_func: Any,
) -> None:
    # Ephemeral cache with singleton base
    cfg = {
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "counter_key": "singleton_ephemeral_cache",
        },
        "ref1": "${base}",
        "ref2": "${base}",
    }

    # this way, the cache is ephemeral.
    x = instantiate_func(cfg)
    assert x.base == (1, "singleton_ephemeral_cache")
    assert x.ref1 == (1, "singleton_ephemeral_cache")
    assert x.ref2 == (1, "singleton_ephemeral_cache")

    x = instantiate_func(cfg)
    assert x.base == (2, "singleton_ephemeral_cache")
    assert x.ref1 == (2, "singleton_ephemeral_cache")
    assert x.ref2 == (2, "singleton_ephemeral_cache")


def test_instantiated_once_persistent_cache(
    instantiate_func: Any,
) -> None:
    # Persistent cache with singleton base
    cfg = {
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "counter_key": "singleton_persistent_cache",
        },
        "ref1": "${base}",
        "ref2": "${base}",
    }

    # this way, the cache is persistent.
    x = instantiate_func(cfg, cache=True)
    assert x.base == (1, "singleton_persistent_cache")
    assert x.ref1 == (1, "singleton_persistent_cache")
    assert x.ref2 == (1, "singleton_persistent_cache")

    x = instantiate_func(cfg, cache=True)
    assert x.base == (1, "singleton_persistent_cache")
    assert x.ref1 == (1, "singleton_persistent_cache")
    assert x.ref2 == (1, "singleton_persistent_cache")


def test_once_invalid_once_type(instantiate_func):
    import hydra.errors
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": ["not", "a", "string"],
        "counter_key": "invalid_once_type",
    }
    with pytest.raises(hydra.errors.InstantiationException):
        instantiate_func(cfg, cache={})


def test_once_false_behaves_as_no_once(instantiate_func):
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": False,
        "counter_key": "test_once_false",
    }
    # Should behave as if _once_ is not present: increment each time
    assert instantiate_func(cfg, cache={}) == (1, "test_once_false")
    assert instantiate_func(cfg, cache={}) == (2, "test_once_false")


def test_missing_target_raises(instantiate_func):
    import hydra.errors
    # Only configs with _once_ present (not False) and missing _target_ should raise
    cfg = {
        "_once_": True,
        "some_key": 123
    }
    with pytest.raises(hydra.errors.InstantiationException):
        instantiate_func(cfg, cache={})
    cfg2 = {
        "_once_": "mykey",
        "some_key": 123
    }
    with pytest.raises(hydra.errors.InstantiationException):
        instantiate_func(cfg2, cache={})
    # Plain dict without _target_ and without _once_ should NOT raise
    cfg3 = {
        "some_key": 123,
        "another": "value"
    }
    instantiate_func(cfg3, cache={})  # should not raise


def test_once_present_and_missing_target_raises(instantiate_func):
    import hydra.errors
    # _once_ True, missing _target_ should raise
    cfg = {
        "_once_": True,
        "some_key": 123
    }
    with pytest.raises(hydra.errors.InstantiationException):
        instantiate_func(cfg, cache={})
    # _once_ string, missing _target_ should raise
    cfg2 = {
        "_once_": "mykey",
        "some_key": 123
    }
    with pytest.raises(hydra.errors.InstantiationException):
        instantiate_func(cfg2, cache={})
    # _once_ False, missing _target_ should NOT raise
    cfg3 = {
        "_once_": False,
        "some_key": 123
    }
    instantiate_func(cfg3, cache={})  # should not raise


def test_once_with_interpolations(instantiate_func):
    from omegaconf import OmegaConf
    cfg = OmegaConf.create({
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "counter_key": "interp_base"
        },
        "ref": "${base}"
    })
    x = instantiate_func(cfg)
    assert x.base == (1, "interp_base")
    assert x.ref == (1, "interp_base")
    y = instantiate_func(cfg)
    assert y.base == (2, "interp_base")
    assert y.ref == (2, "interp_base")


def test_once_thread_safety_global_cache():
    import threading
    from hydra_once import instantiate, clear
    clear()
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "counter_key": "threadsafe"
    }
    results = []
    def worker():
        results.append(instantiate(cfg, cache=True))
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(r == results[0] for r in results)


def test_once_manual_key_collision_warning(instantiate_func):
    # Two different configs with the same manual _once_ key share the singleton
    cfg1 = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": "shared_key_collision",
        "counter_key": "A",
    }
    cfg2 = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": "shared_key_collision",
        "counter_key": "B",
        "extra": 123
    }
    cache = {}
    result1 = instantiate_func(cfg1, cache=cache)
    result2 = instantiate_func(cfg2, cache=cache)
    assert result1 == result2
    # Optionally: warn if configs differ (not implemented, just a note)


def test_once_manual_key_unhashable(instantiate_func):
    import hydra.errors
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": {"unhashable": [1,2,3]},
        "counter_key": "unhashable_key"
    }
    with pytest.raises(Exception):
        instantiate_func(cfg, cache={})


def test_once_missing_target_error_message(instantiate_func):
    import hydra.errors
    cfg = {
        "_once_": True,
        "counter_key": "missing_target"
    }
    with pytest.raises(hydra.errors.InstantiationException) as excinfo:
        instantiate_func(cfg, cache={})
    assert "requires _target_" in str(excinfo.value) or "_target_" in str(excinfo.value)
