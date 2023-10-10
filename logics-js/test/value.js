import assert from "assert";
import Value from "../value.js";

describe("Value", () => {
    
    
    it("None", () => {
        let none = new Value(null);

        // assert.strictEqual(none, null);
        // assert.isNull(none.toNullable());
        // assert.isFalse(none.toBoolean());
        assert.strictEqual(none.toBool(), false);
        assert.strictEqual(none.toInt(), 0);
        assert.strictEqual(none.toFloat(), 0.0);
        assert.strictEqual(none.repr(), "None");
    });

    it("bool", () => {
        let value_true = new Value(true);
        let value_false = new Value(false);
        
        assert.ok(value_true.__cmp__(value_true) == 0);
        assert.ok(value_false.__cmp__(value_false) == 0);
        assert.ok(value_true.__cmp__(new Value(1)) == 0);
        assert.ok(value_false.__cmp__(new Value(0)) == 0);
        assert.strictEqual(value_true.toInt(), 1);
        assert.strictEqual(value_false.toInt(), 0);
        assert.strictEqual(value_true.repr(), "True");
        assert.strictEqual(value_false.repr(), "False");
    });

    it("conversion", () => {       
        
        assert.ok(new Value({"a": 1}).__cmp__(new Value({"a": 1})) == 0);
        assert.ok(new Value(4).__cmp__(new Value(4)) == 0);
        assert.ok(new Value(4).__neg__(2));
        // assert.ok(new Value(4).__add__(4).__cmp__(8));
        // assert.ok(new Value(4).__add__(4) == 8 );
        // assert.ok(new Value(4).__add__(4), 8 );
        // assert.ok(new Value("4112", { optimize: true }).__cmp__("4112") == 0);
        // assert.ok(new Value("4112", { optimize: true }).__cmp__("4112"));
        assert.deepEqual(new Value({ a: 1 }), new Value({ a: 1 }));
        // assert.strictEqual(new Value(4), new Value(4));
        // assert.strictEqual(new Value(4).__cmp__(new Value(4)));
        assert.notStrictEqual(new Value(4), 2);
        // assert.strictEqual(new Value(4).add(4), 8);
        // assert.strictEqual(new Value(4).__add__(4), 8);
        // assert.strictEqual(new Value('4112', { optimize: true }).repr(), '4112');
    });
    
    it("int", () => {       
        const _123 = new Value(123);
        
        assert.strictEqual(_123.toInt(), 123);
        assert.strictEqual(_123.__neg__().toInt(), -123);
        assert.strictEqual(new Value(' 123 xix').toInt(), 123);
        assert.strictEqual(new Value(' -123 xix').toInt(), -123);
        assert.strictEqual(_123.repr(), '123');
        assert.strictEqual(_123.__neg__().repr(), '-123');       
    });
    
    it("float", () => {
        const _1234 = new Value(123.4);
    
        assert.strictEqual(_1234.toFloat(), 123.4);
        assert.strictEqual(_1234.__neg__().toFloat(), -123.4);
        assert.strictEqual(new Value(' 123.4 xfx').toFloat(), 123.4);
        assert.strictEqual(new Value(' 123.4 xfx').toFloat(), 123.4);
        assert.strictEqual(new Value(' -123.4 xfx').toFloat(), -123.4);
        assert.strictEqual(_1234.repr(), '123.4');
        assert.strictEqual(_1234.__neg__().repr(), '-123.4');        
    });
    
});



