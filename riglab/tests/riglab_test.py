from riglab.naming import Manager as NM


def test_NamingConvention():
    nm = NM()
    nm.rule = "3dobject"
    with nm.override(side="L", itemName="foo"):
        assert nm.qn("null") == "foo_000_L_LOC"
        assert nm.qn("jnt") == "foo_000_L_JNT"
        assert nm.qn("curve") == "foo_000_L_LINE"
