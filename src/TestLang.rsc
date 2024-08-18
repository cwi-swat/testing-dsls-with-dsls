module TestLang

import Message;
import util::IDEServices;
import IO;
import List;
import util::Math;

import Check;
import Eval;
import ParseTree;
extend Syntax;

// !A * B -> (!A) * B

start syntax Tests = "title" Str title Test* tests;

syntax Expr = non-assoc CheckMarker "(" Expr ")";

lexical CheckMarker
  = @Category="Constant" "$error"
  | @Category="Constant" "$warning"
  ;

syntax Question 
    = non-assoc CheckMarker "(" Question ")"
    ;

syntax Test
    = "test" Str name Form form
    | "test" Str name "with" {KeyVal ","}* inputs Form form "=" State output
    | "test" Str name "with" {KeyVal ","}* inputs Form form "renders" "as" UI ui;
    
syntax UI
  = "[" Question!ifThen!ifThenElse!block* widgets "]";


syntax State = "{" {KeyVal ","}* keyVals "}";

syntax KeyVal = Id ":" Expr;

alias Spec = tuple[
    str name,
    Form form,
    set[loc] errors,
    set[loc] warnings,
    list[Input] inputs,
    VEnv output,
    list[Question] ui
];

Spec extractSpec(Test t) {
    errors = {};
    warnings = {};
    inputs = [];
    output = ();
    ui = [];

    Form strip(Test t) {
        return visit (t.form) {
            case (Expr)`$error(<Expr e>)`: {
                errors += {e.src};
                insert e;
            }
            case (Expr)`$warning(<Expr e>)`: {
                warnings += {e.src};
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
            case Question _: ;

            case Expr _: ;
        };
    }

    if (t has inputs) {
        inputs = [user("<x>", eval(v, ())) | (KeyVal)`<Id x>: <Expr v>` <- t.inputs ];
    }

    if (t has output) {
        output = ("<x>": eval(v, ()) | (KeyVal)`<Id x>: <Expr v>` <- t.output.keyVals );
    }

    if (t has ui) {
        ui = [ w | Question w <- t.ui.widgets ];
    }
    
    return <"<t.name>"[1..-1], strip(t), errors, warnings, inputs, output, ui>;
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
    
    VEnv venv = ();
    if (t has inputs) {
        venv = initialEnv(t.form);
        for (Input inp <- spec.inputs) {
            venv = eval(t.form, inp, venv);
        }
    }

    if (t has output) {
        if (venv != spec.output) {
            delta += {error("got: <ppVenv(venv)>", t.output.src)};
        }
    }

    if (t has ui) {
        list[Question] ui = render(t.form, venv);
        int expLen = size(spec.ui);
        int gotLen = size(ui);
        for (int i <- [0..min(expLen, gotLen)]) {
            Question exp = spec.ui[i];
            Question got = ui[i];
            if (exp !:= got) {
                delta += {error("incorrect widget, got: <got>", exp.src)};
            }
        }
        for (expLen > gotLen, int i <- [gotLen..expLen]) {
            delta += {error("expected widget, did not get it", spec.ui[i].src)};
        }
        for (gotLen > expLen, int i <- [expLen..gotLen]) {
            delta += {error("unexpected widgets: <intercalate("\n", [ "<q>" | q <- ui[expLen..gotLen]])>", t.name.src)};
        }
    }

    if (delta != {}) {
        delta += {info("test failed", t.name.src)};
    }
    else {
        delta += {info("success", t.name.src)};
    }
    return delta;
}

set[Message] runTests(start[Tests] tests) 
    = { *runTest(t) | Test t <- tests.top.tests };