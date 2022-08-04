import LogicsParser from "./parser.js";
import Value from "./value.js";

/** The Logics VM in JavaScript */
export default class Logics {
    static #parser = new LogicsParser();

    /** Create a new VM with a given piece of code. */
    constructor(src) {
        this.ast = this.constructor.#parser.parse(src);
        this.ast.dump();
        this.functions = {};
    }

    /** Run the VM with a given set of values.
     * Returns the topmost value of the stack, if any. */
    run(values) {
        let stack = [];

        // Push a guaranteed Value
        stack.op0 = function(value) {
            if( !( value instanceof Value ) ){
                value = new Value(value);
            }

            this.push(value);
        }

        // Perform stack operation with one operand
        stack.op1 = function(fn) {
            this.op0(fn(this.pop()));
        }

        // Perform stack operation with two operands
        stack.op2 = function(fn) {
            let b = this.pop();
            this.op0(fn(this.pop(), b));
        }

        this.traverse(this.ast, stack, values || {});
        return stack.pop();
    }

    /**
     * General traversal function.
     *
     * This function performs pre, loop or pass and post operations.
     * @param node
     * @param stack
     * @param values
     */
    traverse(node, stack, values) {
        // This helper function simulates a match-statement like in Rust or Python...
        function action(key, object) {
            let fn;

            if ((fn = object[key]) !== undefined) {
                return fn() ?? true;
            }

            // Rust-like '_' wildcard fallback
            if ((fn = object["_"]) !== undefined) {
                return fn();
            }

            return false;
        }

        // Flow operations
        if (!action(node.emit, {
                "comprehension": () => {
                    console.assert(node.children.length === 3 || node.children.length === 4);
                    this.traverse(node.children[2], stack, values);

                    // obtain the list
                    let list = stack.pop().toList().valueOf();

                    let ret = [];

                    // iterate over list
                    for( let i of list ) {
                        values[node.children[1].match] = i;
                        this.traverse(node.children[0], stack, values);

                        // optional if
                        if (node.children.length === 4) {
                            this.traverse(node.children[3], stack, values);
                            if (!stack.pop().toBool()) {
                                continue;
                            }
                        }
                        ret.push(stack.pop());
                    }

                    // push result list
                    stack.op0(ret);
                },
                "and": () => {
                    console.assert(node.children.length === 2);
                    this.traverse(node.children[0], stack, values);

                    let check = stack.pop();
                    if (check.toBool()) {
                        this.traverse(node.children[1], stack, values);
                    }
                    else {
                        stack.push(check);
                    }
                },
                "if": () => {
                    console.assert(node.children.length === 3);

                    // Evaluate condition
                    this.traverse(node.children[1], stack, values);

                    // Evaluate specific branch
                    if (stack.pop().toBool()) {
                        this.traverse(node.children[0], stack, values);
                    } else {
                        this.traverse(node.children[2], stack, values);
                    }
                },
                "or": () => {
                    console.assert(node.children.length === 2);
                    this.traverse(node.children[0], stack, values);

                    let check = stack.pop();
                    if (!check.toBool()) {
                        this.traverse(node.children[1], stack, values);
                    }
                    else {
                        stack.push(check);
                    }
                },
                "cmp": () => {
                    for (let i = 0; i < node.children.length; i++) {
                        this.traverse(node.children[i], stack, values);

                        if (i === 0) {
                            continue;
                        }

                        let b = stack.pop();
                        let a = stack.pop();

                        let res = action(node.children[i].emit, {
                            "eq": () => a.__cmp__(b) === 0,
                            "gteq": () => a.__cmp__(b) >= 0,
                            "gt": () => a.__cmp__(b) > 0,
                            "lteq": () => a.__cmp__(b) <= 0,
                            "lt": () => a.__cmp__(b) < 0,
                            "neq": () => a.__cmp__(b) !== 0,
                            "_": () => console.log("unreachable"),
                        });

                        // Either push false and break or push b
                        stack.op0(res ? i === node.children.length - 1 ? true : b : false);

                        if (!res) {
                            break;
                        }
                    }
                }
            })) {

            if (node.children !== undefined) {
                // Iterate over children
                for (let child of node.children) {
                    this.traverse(child, stack, values);
                }
            }
        }

        // Stack operations
        return action(node.emit, {
            "False": () => stack.op0(false),
            "Identifier": () => {
                let name = node.match;

                if (name in values) {
                    stack.push(new Value(values[name]));
                }
                else if (name in this.functions) {
                    stack.push(new Value(this.functions[name]));
                }
                else {
                    stack.push(new Value(null));
                }
            },
            "None": () => stack.op0(null),
            "Number": () => stack.op0(parseFloat(node.match)),
            "String": () => stack.op0(node.match.substring(1, node.match.length - 1)), // cut "..." from string.
            "True": () => stack.op0(true),

            "add": () => stack.op2((a, b) => a.__add__(b)),
            "div": () => stack.op2((a, b) => a.__div__(b)),
            "in": () => stack.op2((a, b) => a.__in__(b)),
            "invert": () => stack.op1((a) => a.__invert__()),
            "list": () => stack.op0(stack.splice(-node.children.length).map(item => item.valueOf())),
            "mod": () => stack.op2((a, b) => a.__mod__(b)),
            "mul": () => stack.op2((a, b) => a.__mul__(b)),
            "neg": () => stack.op1((a) => a.__neg__()),
            "not": () => stack.op1((a) => !a.toBool()),
            "outer": () => stack.op2((a, b) => !a.__in__(b)),
            "pos": () => stack.op1((a) => a.__pos__()),
            "pow": () => stack.op2((a, b) => a.__pow__(b)),
            "strings": () => stack.op0(stack.splice(-node.children.length).join("")),
            "sub": () => stack.op2((a, b) => a.__sub__(b)),
        });
    }
}

// Register Logics in the browser
if (window !== undefined) {
    window.Logics = Logics;
}
