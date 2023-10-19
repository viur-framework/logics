import glob, os
import pytest
from logics import Logics

# This parameterized test case loads .lgx files from the "../tests/" directory
# and processes them one by one.
@pytest.mark.parametrize("input", glob.glob("../tests/*.lgx"))
def test_testcase(input):
    # Read the content of the current .lgx file.
    input = open(input, "r").read()
    variables = {}  # Initialize an empty dictionary to store variables
    last_result = None  # Initialize a variable to store the last result

    for line in input.splitlines():
        line = line.strip()

        if not line:
            continue
        elif line[0] == "#":
            # Split the line into components separated by ':'
            cmd = line[1:].split(":", 2)

            action = cmd[0].lower()

            if action == "expect":
                expect = cmd[1]

                # Ensure that the last result is not None and compare it to the expected value
                assert last_result is not None, "#EXPECT used before evaluation"
                assert repr(last_result) == expect
                last_result = None

            elif action == "set":
                var = cmd[1]
                value = cmd[2]

                # Use the Logics class to evaluate the value and update variables
                variables[var] = Logics(value).run(variables)
        else:
            # Evaluate the current line using the Logics class and update last_result
            last_result = Logics(line).run(variables)

    # Ensure that last_result is None (unverified) at the end of the test case
    assert last_result is None, f"{last_result=} unverified"
