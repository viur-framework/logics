import LogicsParser from "./parser.js";
import Value from "./value.js";

/** The Logics VM in JavaScript */
export default class Logics {
    static #parser = new LogicsParser();

    /** Create a new VM with a given piece of code. */
    constructor(src) {
        this.ast = this.constructor.#parser.parse(src);
        this.ast.dump();
        this.functions = {
            "bool": (val) => val.toBool(),
            "currency": (value, decimalDelimiter, thousandsDelimiter, currencySign) => "#todo",  // todo
            "float": (val) => val.toFloat(),
            "int": (val) => val.toInt(),
            "join": (array, delimiter, lastDelimiter) => array.toList().join((delimiter && delimiter.toString()) || ", "),  // fixme: lastDelimiter?
            "keys": (val) => Object.keys(val.toDict().valueOf()),
            "len": (val) => val.__len__(),
            "lfill": (str, len, fill) => str.toString().padStart(len, fill),
            "lower": (str) => str.toString().toLowerCase(),
            "lstrip": (str) => str.toString().trimStart(),
            "max": (array) => Math.max(...array.toList().valueOf().map((i) => parseFloat(i) || 0)),
            "min": (array) => Math.min(...array.toList().valueOf().map((i) => parseFloat(i) || 0)),
            "range": (start, end, step) => [],
            "replace": (str, find, replace) => str.toString().replaceAll((find && find.toString()) || " ", (replace && replace.toString()) || ""),
            "rfill": (str, len, fill) => str.toString().padEnd(len, fill),
            "round": (float, precision) => parseFloat(float.toFloat().toFixed((precision && precision.toInt()) || 0)),
            "rstrip": (str) => str.toString().trimEnd(),
            "split": (str, delimiter) => str.toString().split((delimiter && delimiter.toString()) || " "),
            "str": (val) => val.toString(),
            "strip": (str) => str.toString().trim(),
            "sum": (array) => array.toList().valueOf().map((i) => parseFloat(i) || 0).reduce((total, i) => total + i, 0),
            "upper": (str) => str.toString().toUpperCase(),
            "values": (val) => Object.values(val.toDict().valueOf()),
        };
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

        // Perform stack operation with three operands
        stack.op3 = function(fn) {
            let c = this.pop();
            let b = this.pop();
            this.op0(fn(this.pop(), b, c));
        }

        this.traverse(this.ast, stack, Object.assign({}, values || {}));
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
                "call": () => {
                    let args = [];

                    if (node.children.length === 2) {
                        this.traverse(node.children[1], stack, values);
                        args = stack.pop().toList();
                    }

                    let fn = this.functions[node.children[0].match];

                    if (fn !== undefined) {
                        // Convert all args to Logics values
                        for (let i in args) {
                            args[i] = new Value(args[i]);
                        }

                        stack.op0(fn(...args));
                    }
                    else {
                        throw new Error(`Call to unknown function: ${node.children[0].match}`);
                    }
                },
                "comprehension": () => {
                    /*
                    for (let i = 0; i < node.children.length; i++) {
                        console.log(i, node.children[i]);
                    }
                    */

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

            if (node.children ?? false) {
                // Iterate over children
                for (let child of node.children) {
                    this.traverse(child, stack, values);
                }
            }
        }

        // Stack operations
        return action(node.emit, {
            // Pushing values
            "False": () => stack.op0(false),
            "Identifier": () => stack.op0(node.match),
            "None": () => stack.op0(null),
            "Number": () => stack.op0(parseFloat(node.match)),
            "String": () => stack.op0(node.match.substring(1, node.match.length - 1)), // cut "..." from string.
            "True": () => stack.op0(true),

            // Operations
            "add": () => stack.op2((a, b) => a.__add__(b)),
            "attr": () => stack.op2((name, attr) => name.toDict()[attr]),
            "div": () => stack.op2((a, b) => a.__div__(b)),
            "in": () => stack.op2((a, b) => a.__contains__(b)),
            "invert": () => stack.op1((a) => a.__invert__()),
            "list": () => stack.op0(stack.splice(-node.children.length).map(item => item.valueOf())),
            "mod": () => stack.op2((a, b) => a.__mod__(b)),
            "mul": () => stack.op2((a, b) => a.__mul__(b)),
            "neg": () => stack.op1((a) => a.__neg__()),
            "not": () => stack.op1((a) => !a.toBool()),
            "outer": () => stack.op2((a, b) => !a.__contains__(b)),
            "pos": () => stack.op1((a) => a.__pos__()),
            "pow": () => stack.op2((a, b) => a.__pow__(b)),
            "index": () => stack.op2( (value, idx) => value.__getitem__(idx)),
            "load": () => stack.op1((name) => values[name.toString()]),
            "slice": () => stack.op3( (value, from, to) => value.__getitem__(from, to)),
            "strings": () => stack.op0(stack.splice(-node.children.length).join("")),
            "sub": () => stack.op2((a, b) => a.__sub__(b)),
            "vars": () => stack.op0(values),
        });
    }
}

// Register Logics in the browser
if (window !== undefined) {
    window.Logics = Logics;
}
