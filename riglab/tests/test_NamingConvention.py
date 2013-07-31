from riglab.naming import Manager as NM


def test_explicit():
    nm = NM()
    params = {"itemName": "foo",
              "itemNumber": 5,
              "side": "left",
              "type": "rig",
              "category": "character"}
    assert nm.qn(rule="3dobject", **params) == "foo_005_L_RIG"
    assert nm.qn(rule="model", **params) == "CH_foo_005"


def test_implicit():
    nm = NM()
    nm.rule = "3dobject"
    assert nm.qn("foo", 5, "left", "rig", "character") == "foo_005_L_RIG"
    assert nm.qn("bar", 5, "left", "rig", "character") == "bar_005_L_RIG"
    assert nm.qn("baz", 5, "left", "rig", "character") == "baz_005_L_RIG"
    nm.rule = "model"
    assert nm.qn("foo", 5, "left", "rig", "character") == "CH_foo_005"
    assert nm.qn("bar", 5, "left", "rig", "character") == "CH_bar_005"
    assert nm.qn("baz", 5, "left", "rig", "character") == "CH_baz_005"


def test_context():
    nm = NM()
    with nm.override(side="L", itemName="foo", rule="3dobject"):
        assert nm.qn("null") == "foo_000_L_LOC"
        assert nm.qn("jnt") == "foo_000_L_JNT"
        assert nm.qn("curve") == "foo_000_L_LINE"


def test_defaults():
    nm = NM()
    assert nm.qn("foo") is not None
    assert nm.qn("bar") is not None
    assert nm.qn("baz") is not None
