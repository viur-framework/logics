use std::collections::HashMap;
use num_parse::parse_int;

#[derive(Debug)]
pub enum Value {
    None,
    Bool(bool),
    Int(i64),
    Float(f64),
    String(String),
    List(Vec<Value>),
    Dict(HashMap<Value, Value>),
}

impl Value {
    fn to_bool(&self) -> bool {
        match self {
            Self::None => false,
            Self::Bool(b) => *b,
            Self::Int(i) => *i != 0,
            Self::Float(f) => *f != 0.0,
            Self::String(s) => !s.is_empty(),
            Self::List(l) => !l.is_empty(),
            Self::Dict(d) => !d.is_empty(),
        }
    }

    fn to_i64(&self) -> i64 {
        match self {
            Self::None => 0,
            Self::Bool(b) => {
                if *b {
                    1
                } else {
                    0
                }
            }
            Self::Int(i) => *i,
            Self::Float(f) => *f as i64,
            Self::String(s) => {
                if let Some(i) = parse_int::<i64>(s) {
                    i
                } else {
                    0
                }
            }
            Self::List(l) => todo!(),
            Self::Dict(d) => todo!(),
        }
    }

    fn to_f64(&self) -> f64 {
        match self {
            Self::None => 0.0,
            Self::Bool(b) => {
                if *b {
                    1.0
                } else {
                    0.0
                }
            }
            Self::Int(i) => *i as f64,
            Self::Float(f) => *f,
            Self::String(s) => {
                if let Ok(f) = s.parse::<f64>() {
                    f
                } else {
                    0.0
                }
            }
            Self::List(l) => todo!(),
            Self::Dict(d) => todo!(),
        }
    }

    fn to_string(&self) -> String {
        match self {
            Self::String(s) => s.clone(),
            Self::Float(f) => format!("{}", f),
            other => other.repr(),
        }
    }

    fn repr(&self) -> String {
        match self {
            Self::None => "None".to_string(),
            Self::Bool(b) => {
                if *b {
                    "True".to_string()
                } else {
                    "False".to_string()
                }
            }
            Self::Int(i) => format!("{}", i),
            Self::Float(f) => {
                if f.fract() == 0.0 {
                    format!("{}.0", f)
                }
                else {
                    format!("{}", f)
                }
            }
            Self::String(s) => {
                let mut ret = String::with_capacity(s.len() + 2);
                ret.push('"');

                for ch in s.chars() {
                    match ch {
                        '\\' => ret.push_str("\\\\"),
                        '\"' => ret.push_str("\\\""),
                        '\n' => ret.push_str("\\n"),
                        '\r' => ret.push_str("\\r"),
                        '\t' => ret.push_str("\\t"),
                        ch => ret.push(ch),
                    }
                }

                ret.push('"');
                ret
            }
            Self::List(l) => todo!(),
            Self::Dict(d) => todo!(),
        }
    }
}

#[test]
fn test_none() {
    let none = Value::None;
    assert_eq!(none.to_bool(), false);
    assert_eq!(none.to_i64(), 0i64);
    assert_eq!(none.to_f64(), 0f64);
    assert_eq!(none.to_string(), "None");
    assert_eq!(none.repr(), "None");
}

#[test]
fn test_bool() {
    // True
    let t = Value::Bool(true);

    assert_eq!(t.to_bool(), true);
    assert_eq!(t.to_i64(), 1i64);
    assert_eq!(t.to_f64(), 1f64);
    assert_eq!(t.to_string(), "True");
    assert_eq!(t.repr(), "True");

    // False
    let f = Value::Bool(false);

    assert_eq!(f.to_bool(), false);
    assert_eq!(f.to_i64(), 0i64);
    assert_eq!(f.to_f64(), 0f64);
    assert_eq!(f.to_string(), "False");
    assert_eq!(f.repr(), "False");

    let i = Value::Int(42);
    assert_eq!(i.to_i64(), 42i64);
    assert_eq!(i.to_f64(), 42f64);

    let f = Value::Float(3.1415);
    assert_eq!(f.to_i64(), 3i64);
    assert_eq!(f.to_f64(), 3.1415f64);
}

#[test]
fn test_int() {
    let i = Value::Int(42);
    assert_eq!(i.to_bool(), true);
    assert_eq!(i.to_i64(), 42i64);
    assert_eq!(i.to_f64(), 42f64);
    assert_eq!(i.to_string(), "42");
    assert_eq!(i.repr(), "42");

    let i = Value::Int(0);
    assert_eq!(i.to_bool(), false);
    assert_eq!(i.to_i64(), 0i64);
    assert_eq!(i.to_f64(), 0f64);
    assert_eq!(i.to_string(), "0");
    assert_eq!(i.repr(), "0");
}

#[test]
fn test_float() {
    let f = Value::Float(3.1415);
    assert_eq!(f.to_bool(), true);
    assert_eq!(f.to_i64(), 3i64);
    assert_eq!(f.to_f64(), 3.1415f64);
    assert_eq!(f.to_string(), "3.1415");
    assert_eq!(f.repr(), "3.1415");

    let f = Value::Float(1337f64);
    assert_eq!(f.to_bool(), true);
    assert_eq!(f.to_i64(), 1337i64);
    assert_eq!(f.to_f64(), 1337f64);
    assert_eq!(f.to_string(), "1337");
    assert_eq!(f.repr(), "1337.0");
}

#[test]
fn test_string() {
    let s = Value::String("Hello".to_string());
    assert_eq!(s.to_bool(), true);
    assert_eq!(s.to_i64(), 0i64);
    assert_eq!(s.to_f64(), 0f64);
    assert_eq!(s.to_string(), "Hello");
    assert_eq!(s.repr(), "\"Hello\"");

    let s = Value::String("".to_string());
    assert_eq!(s.to_bool(), false);
    assert_eq!(s.to_i64(), 0i64);
    assert_eq!(s.to_f64(), 0f64);
    assert_eq!(s.to_string(), "");
    assert_eq!(s.repr(), "\"\"");

    let s = Value::String("42".to_string());
    assert_eq!(s.to_bool(), true);
    assert_eq!(s.to_i64(), 42i64);
    assert_eq!(s.to_f64(), 42f64);
    assert_eq!(s.to_string(), "42");
    assert_eq!(s.repr(), "\"42\"");

    let s = Value::String("3.1415".to_string());
    assert_eq!(s.to_bool(), true);
    assert_eq!(s.to_i64(), 3i64);
    assert_eq!(s.to_f64(), 3.1415f64);
    assert_eq!(s.to_string(), "3.1415");
    assert_eq!(s.repr(), "\"3.1415\"");
}
