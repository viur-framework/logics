import LogicsParser from "./parser.js";

/** Wrapper for JavaScript values in the Logics VM, emulating
 * Python-style values and JSON-serializable objects. */
export class Value {
    #value;  // private property: The native value
    #type;  // private property: Logics type name

    constructor(value) {
        if (value instanceof Value) {
            this.#value = value.valueOf();
            this.#type = value.type();
        }
        else {
            this.#value = value;
            this.#type = this.type();
        }
    }

    /// Return value's native JS value
    valueOf() {
        return this.#value;
    }

    /// Returns the Logics value type; The type is cached in this.#type, for further usage.
    type() {
        if (this.#type !== undefined) {
            return this.#type;
        }

        switch (typeof this.#value) {
            case "undefined":
                return "NoneType";

            case "boolean":
                return "bool";

            case "number":
                if (this.#value % 1 === 0) {
                    return "int";
                }

                return "float";

            case "string":
                return "str";

            case "object":
                // Check if every item of the array has a valid Logics type.
                if (this.#value instanceof Array) {
                    for (let item of this.#value) {
                        if (!Value.prototype.type.call(item)) {
                            throw new Error("Cannot fully convert Array into a valid Logics type");
                        }
                    }

                    return "list";
                }
                else if (this.#value === null) {
                    return "NoneType";
                }

                // Check if every property of the object has a valid Logics type.
                for (let key of Object.keys(value)) {
                    if (!Value.prototype.type.call(value[key])) {
                        throw new Error("Cannot fully convert Object into a valid Logics type");
                    }
                }

                return "dict";
        }
    }

    /// Return the value's representation
    repr() {
        switch (this.type()) {
            case "NoneType":
                return "None";

            case "bool":
                return this.#value ? "True" : "False";

            case "int":
            case "float":
                return this.#value.toString();

            case "str":
                return "\"" + this.#value.toString().replace("\"", "\\\"") + "\"";

            case "list":
               return "[" +
                    this.#value.map(
                        item => {
                            if (!item instanceof Value) {
                                item = new Value(item);
                            }

                            return item.repr()
                        }
                    ).join(", ") + "]";

            case "dict":
                return "{" +
                    Object.keys(this.#value).map(
                        key => {
                            if (!key instanceof Value) {
                                key = new Value(key);
                            }

                            let value = this.#value[key];
                            if (!value instanceof Value) {
                                value = new Value(value);
                            }

                            return key + ": " + value.repr()
                        }
                    ).join(", ") + "}";

            default:
                throw new Error("Unimplemented repr for " + this.type());
        }
    }

    /**
     * Convert Value as Logics string representation.
     */
    toString() {
        switch (this.type()) {
            case "str":
            case "float":
            case "int":
                return this.#value.toString();

            default:
                return this.repr();
        }
    }

    // Returns JS-native boolean value.
    toBool() {
        return Boolean(this.#value);
    }

    // Returns JS-native int value.
    toInt() {
        if (this.#value === true) {
            return 1;
        }

        return parseInt(this.#value) || 0;
    }

    // Returns JS-native float value.
    toFloat() {
        if (this.#value === true) {
            return 1.0;
        }

        return parseFloat(this.#value) || 0.0;
    }

    // Returns JS-native list value.
    toList() {
        let type = this.type();

        if (type === "list") {
            return this.#value;
        }
        else if (type) {
            return [this.#value];
        }

        return null;
    }

    // Returns JS-native dict value.
    toDict() {
        let type = this.type();

        if (type === "dict") {
            return this.#value;
        }
        else if (type) {
            let dict = {};
            dict[this.#value] = this.#value;
            return dict;
        }

        return null;
    }

    // Performs an add-operation with another Value object.
    add(op) {
        if( this.type() === "str" || op.type() === "str" ) {
            return new Value(this.toString() + op.toString());
        }

        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() + op.toFloat());
        }

        return new Value(this.toInt() + op.toInt());
    }

    // Performs a sub-operation with another Value object.
    sub(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() - op.toFloat());
        }

        return new Value(this.toInt() - op.toInt());
    }

    // Performs a mul-operation with another Value object.
    mul(op) {
        if (this.type() === "str") {
            return new Value(this.toString().repeat(op.toInt()));
        }
        else if (op.type() === "str") {
            return new Value(op.toString().repeat(this.toInt()));
        }

        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() * op.toFloat());
        }

        return new Value(this.toInt() * op.toInt());
    }

    // Performs a div-operation with another Value object.
    div(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() / op.toFloat());
        }

        return new Value(this.toInt() / op.toInt());
    }

    // Performs a mod-operation with another Value object.
    mod(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() % op.toFloat());
        }

        return new Value(this.toInt() % op.toInt());
    }

    // Performs unary plus
    pos() {
       if (this.type() === "float") {
           return new Value(+this.toFloat());
       }

       return new Value(+this.toInt());
    }

    // Performs unary minus
    neg() {
       if (this.type() === "float") {
           return new Value(-this.toFloat());
       }

       return new Value(-this.toInt());
    }

    // Performs unary complement
    compl() {
       return new Value(~this.toInt());
    }
}

/** The Logics VM in JavaScript */
export default class Logics {
    static #parser = new LogicsParser();

    /** Create a new VM with a given piece of code. */
    constructor(src) {
        this.ast = this.constructor.#parser.parse(src);
        this.functions = {};
    }

    /** Run the VM with a given set of values.
     * Returns the topmost value of the stack, if any. */
    run(values) {
        let stack = [];
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
        let fn;

        if ((fn = this["pre_" + node.emit]) !== undefined) {
            fn.call(this, node, stack, values);
        }

        if ((fn = this["loop_" + node.emit]) !== undefined) {
            fn.call(this, node, stack, values);
        }
        else if (node.children !== undefined) {
            let fn = this["pass_" + node.emit];

            for (let child of node.children) {
                this.traverse(child, stack, values);

                if (fn !== undefined) {
                    fn.call(this, node, stack, values);
                }
            }
        }

        if ((fn = this["post_" + node.emit]) !== undefined) {
            fn.call(this, node, stack, values);
        }
    }

    post_STRING(node, stack) {
        // Cut "..." from string.
        stack.push(new Value(node.match.substring(1, node.match.length - 1)));
    }

    post_concat(node, stack) {
        stack.push(new Value(stack.splice(-node.children.length).join("")));
    }

    post_list(node, stack) {
        stack.push(new Value(stack.splice(-node.children.length)));
    }

    post_NUMBER(node, stack) {
        stack.push(new Value(parseFloat(node.match)));
    }

    post_IDENT(node, stack, values) {
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
    }

    post_add(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.add(b));
    }

    post_mul(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.mul(b));
    }

    post_sub(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.sub(b));
    }

    post_div(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.div(b));
    }

    post_mod(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.mod(b));
    }

    post_plus(node, stack) {
        stack.push(stack.pop().pos());
    }

    post_minus(node, stack) {
        stack.push(stack.pop().neg());
    }

    post_complement(node, stack) {
        stack.push(stack.pop().compl());
    }

    post_True(_, stack) {
        stack.push(new Value(true));
    }

    post_False(_, stack) {
        stack.push(new Value(false));
    }

    post_null(_, stack) {
        stack.push(new Value(null));
    }
}

if (window !== undefined) {
    window.Logics = Logics;
}
