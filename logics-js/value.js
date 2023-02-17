/** Wrapper for JavaScript values in the Logics VM, emulating Python-style values and JSON-serializable objects. */
export default class Value {
    #value;  // private property: The native value in JavaScript
    #type;  // private property: Logics type name

    /** Constructs a Logics value from a native JS-value, or clones an existing Logics value.
    In case the native value is not JSON-serializable, an Exception is thrown. */
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

    // Retrieve length of object
    __len__() {
        switch (this.type()) {
            case "dict":
                return Object.keys(this.#value).length;
            case "list":
                return this.#value.length;
            default:
                return this.toString().length;
        }
    }

    // Checks if a given value is part of another value
    __contains__(value) {
        if (value.type() === "dict") {
            return value.valueOf()[this.toString()] !== undefined;  // fixme: toString() conversion falsifies data
        }
        else if (value.type() === "list") {
            // We need to compare every item using __cmp__()
            for(let item of value.valueOf()) {
                item = new Value(item);
                if(item.__cmp__(this) === 0) {
                    return true;
                }
            }

            return false;
            //return new Value(value.valueOf().indexOf(this.valueOf()) >= 0);
        }

        return value.toString().indexOf(this.toString()) >= 0;
    }

    // Index into value
    __getitem__(key, until) {  // todo: provide and use a Slice() class similar to Python (not an until value)
        if (this.type() === "dict") {
            console.assert(until === undefined, "Cannot slice into a dict");
            return this.toDict()[key.toString()];
        }

        let val = this.type() === "list" ? this.toList() : this.toString();

        // Slice-mode
        let from = key.valueOf() === null ? 0 : key.toInt();

        // if from is lower 0, calculate from end.
        if (from < 0) {
            from = val.length + from;
        }

        // Direct index
        if (until === undefined) {
            return val[from];
        }

        // if to is lower 0, calculate from end.
        let to = until.valueOf() === null ? val.length : until.toInt();

        if (to < 0) {
            to = val.length + to;
        }

        return val.slice(from, to);
    }

    // Compare
    __cmp__(other) {
        let a, b;

        // Dict types
        if (this.type() === "dict" || other.type() === "dict") {
            // fixme: Python cannot compare < and > on dict, only ==. Change this here, too?
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
    __truediv__(op) {
        if( this.type() === "float" || op.type() === "float" ) {
            return new Value(this.toFloat() / op.toFloat());
        }

        return new Value(this.toInt() / op.toInt());
    }

    __floordiv__(op) {
        return new Value(Math.floor(this.toInt() / op.toInt()));
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
