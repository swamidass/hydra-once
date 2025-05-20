from pytest import fixture
from typing import Any

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
    # standard behiavior calls target every time
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "key": "test1",  # key is pass through as second return by counter_function
    }
    assert instantiate_func(cfg, cache=cache) == (1, "test1")
    assert instantiate_func(cfg, cache=cache) == (2, "test1")


def test_instantiated_once_keyword(
    instantiate_func: Any,
) -> None:
    # once behavior calls target only once
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "key": "test2",
    }

    assert instantiate_func(cfg, cache=cache) == (1, "test2")
    assert instantiate_func(cfg, cache=cache) == (1, "test2")


def test_instantiated_once_manual_key1(
    instantiate_func: Any,
) -> None:
    # With manual key, gives same value, even if config changes.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": "key1",
        "key": "test3",  # reusing key does not
    }
    assert instantiate_func(cfg, cache=cache) == (1, "test3")
    assert instantiate_func(cfg, cache=cache) == (1, "test3")

    cfg["key"] = "test3-changed"
    cfg["disallowed_arg"] = "broken"
    assert instantiate_func(cfg, cache=cache) == (1, "test3")
    assert instantiate_func(cfg, cache=cache) == (1, "test3")



def test_instantiated_once_auto_key(
    instantiate_func: Any,
) -> None:
    # With auto key, change to the config makes new call.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "key": "test4",  # reusing key does not
    }
    assert instantiate_func(cfg, cache=cache) == (1, "test4")
    assert instantiate_func(cfg, cache=cache) == (1, "test4")

    cfg["key"] = "test4-changed"
    assert instantiate_func(cfg, cache=cache) == (1, "test4-changed")
    assert instantiate_func(cfg, cache=cache) == (1, "test4-changed")


def test_instantiated_once_partial_change(
    instantiate_func: Any,
) -> None:
    # Changing _partial_ makes new signature for auto key.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "key": "test5",
    }
    instance = instantiate_func(cfg, cache=cache)
    assert instantiate_func(cfg, cache=cache) == (1, "test5")

    # setting as default does nothing
    # this behaivior can be removed in the future if code base changes.
    cfg["_partial_"] = False
    assert instantiate_func(cfg, cache=cache) is instance

    # changing busts the key
    cfg["_partial_"] = True
    assert instantiate_func(cfg, cache=cache) is not instance

    instance = instantiate_func(cfg, cache=cache)
    assert instance() == (2, "test5")  # return is being called now!
    assert instance() == (3, "test5")


def test_instantiated_once_recursive_change(
    instantiate_func: Any,
) -> None:
    # Changing _recursive_ makes new signature for auto key.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "key": "test6",
    }
    instance = instantiate_func(cfg, cache=cache)
    assert instance is instantiate_func(cfg, cache=cache)

    # setting as default does nothing
    # this behaivior can be removed in the future if code base changes.
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
        "key": "test7",
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
    # Changing _targe_ makes new signature for auto key.
    cfg = {
        "_target_": "tests.instantiate.counter_function",
        "_once_": True,
        "key": "test8",
    }
    assert instantiate_func(cfg, cache=cache) == (1, "test8")

    cfg["_target_"] = "tests.instantiate.counter_function2"
    assert instantiate_func(cfg, cache=cache) == (2, "test8", "counter_function2")
    assert instantiate_func(cfg, cache=cache) == (2, "test8", "counter_function2")


def test_instantiated_once_nested(
    instantiate_func: Any,
) -> None:
    # Changing _recursive_ makes new signature for auto key.
    cfg = {
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "key": "test9",
        },
        "ref1": "${base}",
        "ref2": "${base}",
    }
    x = instantiate_func(cfg, cache=cache)
    assert x.base == (1, "test9")
    assert x.ref1 == (1, "test9")
    assert x.ref2 == (1, "test9")

    x = instantiate_func(cfg, cache=cache)
    assert x.base == (1, "test9")
    assert x.ref1 == (1, "test9")
    assert x.ref2 == (1, "test9")


def test_instantiated_once_custom_cache(
    instantiate_func: Any,
) -> None:
    # Changing _recursive_ makes new signature for auto key.
    cfg = {
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "key": "test10",
        },
        "ref1": "${base}",
        "ref2": "${base}",
    }

    # you can specify a custom cache too.

    x = instantiate_func(cfg, cache=cache)
    assert x.base == (1, "test10")
    assert x.ref1 == (1, "test10")
    assert x.ref2 == (1, "test10")

    x = instantiate_func(cfg, cache=cache)
    assert x.base == (1, "test10")
    assert x.ref1 == (1, "test10")
    assert x.ref2 == (1, "test10")


def test_instantiated_once_ephemeral_cache(
    instantiate_func: Any,
) -> None:
    # Changing _recursive_ makes new signature for auto key.
    cfg = {
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "key": "test12",
        },
        "ref1": "${base}",
        "ref2": "${base}",
    }

    # this way, the is cache is ephermeral.
    x = instantiate_func(cfg)
    assert x.base == (1, "test12")
    assert x.ref1 == (1, "test12")
    assert x.ref2 == (1, "test12")

    x = instantiate_func(cfg)
    assert x.base == (2, "test12")
    assert x.ref1 == (2, "test12")
    assert x.ref2 == (2, "test12")


def test_instantiated_once_persistent_cache(
    instantiate_func: Any,
) -> None:
    # Changing _recursive_ makes new signature for auto key.
    cfg = {
        "base": {
            "_target_": "tests.instantiate.counter_function",
            "_once_": True,
            "key": "test13",
        },
        "ref1": "${base}",
        "ref2": "${base}",
    }

    # this way, the is cache is persistent.
    x = instantiate_func(cfg, cache=True)
    assert x.base == (1, "test13")
    assert x.ref1 == (1, "test13")
    assert x.ref2 == (1, "test13")

    x = instantiate_func(cfg, cache=True)
    assert x.base == (1, "test13")
    assert x.ref1 == (1, "test13")
    assert x.ref2 == (1, "test13")
