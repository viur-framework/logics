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
            this.#type = this.constructor.type(value);
        }
    }

    /// Return value's native JS value
    valueOf() {
        return this.#value;
    }

    /// Returns the Logics value type; The type is cached in this.#type, for further usage.
    type() {
        return this.#type || (this.#type = this.constructor.type(this.#value))
    }

    /// Determine Logics value type from a JavaScript native value
    static type(value) {
        switch (typeof value) {
            case "undefined":
                return "NoneType";

            case "boolean":
                return "bool";

            case "number":
                if (value % 1 === 0) {
                    return "int";
                }

                return "float";

            case "string":
                return "str";

            case "object":
                // Check if every item of the array has a valid Logics type.
                if (value instanceof Array) {
                    for (let item of value) {
                        if (!this.type(item)) {
                            throw new Error("Cannot fully convert Array into a valid Logics type");
                        }
                    }

                    return "list";
                }
                else if (value === null) {
                    return "NoneType";
                }

                // Check if every property of the object has a valid Logics type.
                for (let key of Object.keys(value)) {
                    if (!this.type(value[key])) {
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
                            if (!( item instanceof Value )) {
                                item = new Value(item);
                            }

                            return item.repr()
                        }
                    ).join(", ") + "]";

            case "dict":
                return "{" +
                    Object.keys(this.#value).map(
                        key => {
                            if (!( key instanceof Value)) {
                                key = new Value(key);
                            }

                            let value = this.#value[key];
                            if (!(value instanceof Value)) {
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

    // Get index
    __getitem__(index) {
        if( this.type() === "dict" ) {
            return new Value(this.#value[index.toString()]);
        }
        else if( this.type() === "list" || this.type() === "str" ) {
            return new Value(this.#value[index.toInt()]);
        }

        return new Value(null);
    }

    // Checks if a given value is part of another value
    __in__(value) {
        if (value.type() === "dict") {
            return value.valueOf()[this.toString()] !== undefined;
        }
        else if (value.type() === "list") {
            // We need to compare every item using __cmp__()
            for(let item of value.valueOf()) {
                item = new Value(item);
                if(item.__cmp__(this) === "eq") {
                    return true;
                }
            }

            return false;
            //return new Value(value.valueOf().indexOf(this.valueOf()) >= 0);
        }

        return value.toString().indexOf(this.toString()) >= 0;
    }

    // Compare
    __cmp__(other) {
        let a, b;

        // Dict types
        if (this.type() === "dict" || other.type() === "dict") {
            a = this.toDict();
            b = other.toDict();

            let ak = Object.keys(a);
            let bk = Object.keys(b);

            if (ak.length < bk.length) {
                return -1;
            }
            else if (ak.length > bk.length) {
                return 1;
            }

            for( let k of ak ) {
                if( typeof b[k] === "undefined" ) {
                    return 1;
                }

                let av = new Value(a[k]);
                let bv = new Value(b[k]);

                let res;
                if ((res = av.__cmp__(bv)) !== 0) {
                    return res;
                }
            }

            return 0;
        }
        // List types
        else if (this.type() === "list" || other.type() === "list") {
            a = this.toList();
            b = other.toList();

            if (a.length < b.length) {
                return -1;
            }
            else if (a.length > b.length) {
                return 1;
            }

            for(let i = 0; i < a.length; i++) {
                let av = new Value(a[i]);
                let bv = new Value(b[i]);

                let res;
                if ((res = av.__cmp__(bv)) !== 0) {
                    return res;
                }
            }

            return 0;
        }
        // Other types
        else if (this.type() === "str" || other.type() === "str") {
            a = this.toString();
            b = other.toString();
        }
        else if (this.type() === "float" || other.type() === "float") {
            a = this.toFloat();
            b = other.toFloat();
        }
        else {
            a = this.toInt();
            b = other.toInt();
        }

        // Perform final comparison
        if (a < b) {
            return -1;
        }
        else if (a > b) {
            return 1;
        }

        return 0;
    }

    // Performs an add-operation with another Value object.
    __add__(op) {
        if( this.type() === "str" || op.type() === "str" ) {
            return new Value(this.toString() + op.toString());
        }

        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() + op.toFloat());
        }

        return new Value(this.toInt() + op.toInt());
    }

    // Performs a sub-operation with another Value object.
    __sub__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() - op.toFloat());
        }

        return new Value(this.toInt() - op.toInt());
    }

    // Performs a mul-operation with another Value object.
    __mul__(op) {
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
    __div__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() / op.toFloat());
        }

        return new Value(this.toInt() / op.toInt());
    }

    // Performs a mod-operation with another Value object.
    __mod__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() % op.toFloat());
        }

        return new Value(this.toInt() % op.toInt());
    }

    // Performs a mod-operation with another Value object.
    __pow__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() ** op.toFloat());
        }

        return new Value(this.toInt() ** op.toInt());
    }

    // Performs unary plus
    __pos__() {
       if (this.type() === "float") {
           return new Value(+this.toFloat());
       }

       return new Value(+this.toInt());
    }

    // Performs unary minus
    __neg__() {
       if (this.type() === "float") {
           return new Value(-this.toFloat());
       }

       return new Value(-this.toInt());
    }

    // Performs unary complement
    __invert__() {
       return new Value(~this.toInt());
    }
}

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
        else if (node.children) {
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

    // AST traversal functions

    post_STRING(node, stack) {
        // Cut "..." from string.
        stack.push(new Value(node.match.substring(1, node.match.length - 1)));
    }

    post_concat(node, stack) {
        stack.push(new Value(stack.splice(-node.children.length).join("")));
    }

    post_list(node, stack) {
        stack.push(new Value(stack.splice(-node.children.length).map(item => item.valueOf())));
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
        stack.push(a.__add__(b));
    }

    post_mul(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.__mul__(b));
    }

    post_sub(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.__sub__(b));
    }

    post_div(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.__div__(b));
    }

    post_mod(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.__mod__(b));
    }

    post_pow(node, stack) {
        let b = stack.pop();
        let a = stack.pop();
        stack.push(a.__pow__(b));
    }

    post_pos(node, stack) {
        stack.push(stack.pop().__pos__());
    }

    post_neg(node, stack) {
        stack.push(stack.pop().__neg__());
    }

    post_invert(node, stack) {
        stack.push(stack.pop().__invert__());
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

    post_cmp(node, stack) {
        for(let i = 1; i < node.children.length; i += 2) {
            let op = node.children[i].emit;
            let right = stack.pop();
            let left = stack.pop();

            let res;

            switch (op) {
                case "in":
                    res = left.__in__(right);
                    console.log("-->", op, left, right, res);
                    break;

                case "not_in":
                    res = !left.__in__(right);
                    console.log("-->", op, left, right, res);
                    break;

                default:
                    res = left.__cmp__(right);
                    console.log("-->", op, left, right, res);

                    switch (op) {
                        case "<":
                            res = res < 0;
                            break;

                        case ">":
                            res = res > 0;
                            break;

                        case "<=":
                            res = res <= 0;
                            break;

                        case ">=":
                            res = res >= 0;
                            break;

                        case "==":
                            res = res === 0;
                            break;

                        case "!=":
                        case "<>":
                            res = res !== 0;
                            break;

                        default:
                            throw SyntaxError("Unhandled operator: " + op)
                    }
            }

            stack.push(new Value(res));
        }
    }
}

if (window !== undefined) {
    window.Logics = Logics;
}
