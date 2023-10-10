// Import necessary Node.js modules and the Logics class.
import fs from "fs";     	// For reading files.
import glob from "glob"; 	// For searching files using a pattern.
import assert from "assert"; // For assertion tests.
import Logics from "../logics.js"; // Assuming the Logics class is defined in "../logics.js".


// This function performs the testing process.
function testcase(code) {
  let variables = {}; 	// Initialize an empty object for variables.
  let lastResult = undefined; // Store the last result.


  // Iterate through each line in the given code.
  for (let line of code.split("\n")) {
	line = line.trim(); // Remove leading and trailing whitespace.


	if (!line) {
  	continue; // Skip empty lines.
	}


	if (line[0] === "#") {
  	// Process lines starting with "#" (comments and instructions).
  	let cmd = line.substr(1).split(":", 3);
  	switch (cmd[0].toLowerCase()) {
    	case "expect":
      	// Verify the expected result.
      	let expect = cmd[1];


      	// Ensure that the previous result is not undefined.
      	assert.notStrictEqual(lastResult, undefined);


      	// Compare the expected result with the last result.
      	assert.strictEqual(lastResult.repr(), expect);


      	// Reset the last result.
      	lastResult = undefined;
      	break;


    	case "set":
      	// Set a variable.
      	let name = cmd[1];
      	let value = cmd[2];


      	// Calculate the variable's value and store it in the variables object.
      	variables[name] = new Logics(value).run(variables);
      	break;
  	}
	} else {
  	// Process lines with expressions.
  	lastResult = new Logics(line).run(variables);
	}
  }


  // Ensure that the last result is undefined (all expected results verified).
  assert.strictEqual(lastResult, undefined, `lastResult=${lastResult} unverified`);
}


// Mocha test description: "Logics" is the name of the test suite.
describe("Logics", () => {
  // Use "glob.sync" to find all .lgx files in the "../tests/" directory.
  const tests = glob.sync("../tests/*.lgx");


  // Create a Mocha test case for each found test file.
  tests.forEach((filename) => it(filename, () => {
	// Read the content of the test file and execute the test.
	testcase(fs.readFileSync(filename, "utf-8"));
  }));
});





