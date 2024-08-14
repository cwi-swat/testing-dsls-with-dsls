module TestLang

import Message;
import util::IDEServices;
import IO;
import List;

import Check;
import Eval;
import ParseTree;
extend Syntax;

// !A * B -> (!A) * B

start syntax Tests = Test* tests;

syntax Expr = non-assoc CheckMarker "(" Expr ")";

lexical CheckMarker
  = @Category="Constant" "$error"
  | @Category="Constant" "$warning"
  ;

syntax Question 
    = non-assoc CheckMarker "(" Question ")"
    ;

syntax Name 
    = non-assoc "$use" "(" Name ")"
    | non-assoc "$def" "(" Name ")"
    ;

syntax Test
    = "test" Str name Form form
    | "test" Str name "with" {KeyVal ","}* inputs Form form "=" State output;

syntax State = "{" {KeyVal ","}* keyVals "}";

syntax KeyVal = Id ":" Expr;

alias Spec = tuple[
    str name,
    Form form,
    set[loc] uses,
    set[loc] defs,
    set[loc] errors,
    set[loc] warnings,
    list[Input] inputs,
    VEnv output
];

Spec extractSpec(Test t) {
    uses = {};
    defs = {};
    errors = {};
    warnings = {};
    inputs = [];
    output = ();

    Form strip(Test t) {
        return visit (t.form) {
            case (Expr)`$error(<Expr e>)`: {
                errors += {e.src};
                insert e;
            }
            case (Question)`$error(<Question q>)`: {
                errors += {q.src};
                insert q;
            }
            case (Question)`$warning(<Question q>)`: {
                warnings += {q.src};
                insert q; 
            }
            case (Name)`$use(<Name n>)`: {
                uses += {n.src};
                insert n;
            }
            case (Name)`$def(<Name n>)`: {
                defs += {n.src};
                insert n;
            }
        };
    }

    if (t has inputs) {
        inputs = [user("<x>", eval(v, ())) | (KeyVal)`<Id x>: <Expr v>` <- t.inputs ];
        output = ("<x>": eval(v, ()) | (KeyVal)`<Id x>: <Expr v>` <- t.output.keyVals );
    }
    
    return <"<t.name>"[1..-1], strip(t), uses, defs, errors, warnings, inputs, output>;
}

str ppValue(vint(int n)) = "<n>";
str ppValue(vstr(str s)) = "\"<s>\"";
str ppValue(vbool(bool b)) = "<b>";

str ppVenv(VEnv venv) = "{<intercalate(", ", lst)>}"
    when lst := [ "<x>: <ppValue(venv[x])>" | str x <- venv ];


set[Message] runTest(Test t) {
    Spec spec = extractSpec(t);
    
    set[Message] msgs = check(spec.form);
    delta = {};
    delta += {error("unexpected error: <s>", l) | error(str s, loc l) <- msgs, l notin spec.errors };
    delta += {error("unexpected warning: <s>", l) | warning(str s, loc l) <- msgs, l notin spec.warnings};
    delta += {error("expected an error", l) | loc l <- spec.errors, !(error(_, l) <- msgs)};
    delta += {error("expected a warning", l) | loc l <- spec.warnings, !(warning(_, l) <- msgs)};
    
    if (t has inputs) {
        venv = initialEnv(t.form);
        for (Input inp <- spec.inputs) {
            venv = eval(t.form, inp, venv);
        }
        if (venv != spec.output) {
            delta += {error("got: <ppVenv(venv)>", t.output.src)};
        }
    }
    if (delta != {}) {
        delta += {info("test failed", t.name.src)};
    }
    return delta;
}

set[Message] runTests(start[Tests] tests) 
    = { *runTest(t) | Test t <- tests.top.tests };