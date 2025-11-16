import glob, os
import pytest
from logics import Logics


@pytest.mark.parametrize("input", glob.glob("../tests/*.lgx"))
def test_testcase(input):
    input = open(input, "r").read()
    variables = {}
    last_line = last_result = None

    for row, line in enumerate(input.splitlines()):
        line = line.strip()

        if not line:
            continue
        elif line[0] == "#":
            cmd = line[1:].split(":", 2)

            action = cmd[0].lower()
            if action == "expect":
                expect = ":".join(cmd[1:])

                assert last_result is not None, "#EXPECT used before evaluation"

                if repr(last_result) != expect:
                    raise AssertionError(f"{row=}: {last_line!r}: {last_result!r} != {expect!r}")

                last_result = None

            elif action == "set":
                var = cmd[1]
                value = cmd[2]
                variables[var] = Logics(value).run(variables)
        else:
            last_result = Logics(line).run(variables)
            last_line = line

    assert last_result is None, f"{last_result=} unverified"
