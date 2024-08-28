module TestLang

import Message;
import util::IDEServices;
import IO;
import List;
import util::Math;
import lang::html::AST;
import lang::html::IO;
import util::Highlight;
import String;

import Check;
import Eval;
import ParseTree;
extend Syntax;

start syntax Tests = Section* sections;

syntax Section = @Foldable "section" Str title Test* tests;

syntax Expr = non-assoc CheckMarker "(" Expr ")";

lexical CheckMarker
  = @Category="Constant" "$error"
  | @Category="Constant" "$warning"
  ;

syntax Question 
    = non-assoc CheckMarker "(" Question ")"
    ;

syntax Test
    = @Foldable "test" Str name Form form
    | @Foldable "test" Str name "with" {KeyVal ","}* inputs Form form "=" State output
    | @Foldable "test" Str name "with" {KeyVal ","}* inputs Form form "renders" "as" UI ui;
    
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
    list[Question] ui,
    map[str,int] dist
];

Spec extractSpec(Test t) {
    set[loc] errors = {};
    set[loc] warnings = {};
    list[Input] inputs = [];
    map[str, Value] output = ();
    list[Question] ui = [];

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
    
    Form theForm = strip(t);
    map[str, int] dist = distribution([ x | /prod(label(str x, _), _, _) := theForm, x != "whitespace" ]);

    return <"<t.name>"[1..-1], theForm , errors, warnings, inputs, output, ui, dist>;
}

str ppValue(vint(int n)) = "<n>";
str ppValue(vstr(str s)) = "\"<s>\"";
str ppValue(vbool(bool b)) = "<b>";

str ppVenv(VEnv venv) = "{<intercalate(", ", lst)>}"
    when lst := [ "<x>: <ppValue(venv[x])>" | str x <- venv ];


set[Message] runTest(Test t, Spec spec) {
    set[Message] delta = {};
    
    try {
        set[Message] msgs = check(spec.form);
        delta += {error("unexpected error <s>", l) | error(str s, loc l) <- msgs, l notin spec.errors };
        delta += {error("unexpected warning <s>", l) | warning(str s, loc l) <- msgs, l notin spec.warnings};
        delta += {error("expected an error", l) | loc l <- spec.errors, !(error(_, l) <- msgs)};
        delta += {error("expected a warning", l) | loc l <- spec.warnings, !(warning(_, l) <- msgs)};
    }
    catch value e: {
        delta += {error("exception during checking: <e>", t.name.src)};
    }
    
    VEnv venv = ();

    try {
        if (t has inputs) {
            venv = initialEnv(t.form);
            for (Input inp <- spec.inputs) {
                venv = eval(t.form, inp, venv);
            }
        }
    }
    catch value e: {
        delta += {error("exception during eval: <e>", t.inputs.src)};
    }

    if (t has output) {
        if (venv != spec.output) {
            delta += {error("got <ppVenv(venv)>", t.output.src)};
        }
    }

    // todo: catch exceptions and add as test-level errors.
    // todo: don't do title, but sections in test files. 

    if (t has ui) {
        list[Question] ui = [];
        try {
            ui = render(t.form, venv);
        }
        catch value e: {
            delta += error("exception during rendering: <e>", t.ui.src);
        }

        int expLen = size(spec.ui);
        int gotLen = size(ui);
        for (int i <- [0..min(expLen, gotLen)]) {
            Question exp = spec.ui[i];
            Question got = ui[i];
            if (exp !:= got) {
                delta += {error("incorrect widget, got <got>", exp.src)};
            }
        }
        for (expLen > gotLen, int i <- [gotLen..expLen]) {
            delta += {error("expected widget, did not get it", spec.ui[i].src)};
        }
        for (gotLen > expLen, int _ <- [expLen..gotLen]) {
            delta += {error("unexpected widgets <intercalate("\n", [ "<q>" | q <- ui[expLen..gotLen]])>", t.name.src)};
        }
    }

    if (delta != {}) {
        delta += {info("test failed", t.name.src)};
    }

    return delta;
}

// t=#start[Form] { x |   /prod(label(str x, _), _, _) := t.definitions });
// [ x | /prod(label(str x, _), _, _) := pt, x != "whitespace" ]

HTMLElement testResult2HTML(Test t, set[Message] msgs) {
    HTMLElement elt = div([]);
    
    HTMLElement title = span([text(capitalize("<t.name>"[1..-1]) + (msgs == {} ? " ✅" : " ❌"))]);
    // HTMLElement title = span([text(capitalize("<t.name>"[1..-1]) + (msgs == {} ? " 	&#x2705;" : " &#x274C;"))]);

    elt.elems += [h3([title])];

    if (t has inputs) {
        elt.elems += [h4([text("When given as input:")])];
        
        list[HTMLElement] rows = [];
        for ((KeyVal)`<Id x>: <Expr v>`<- t.inputs) {
            rows += [tr([td([text("<x>")]), td([text("<v>")])])];
        }
        
        HTMLElement tbl = table([thead([tr([th([text("Question")]), th([text("Value")])])]), tbody(rows)]);
        elt.elems += [tbl];
    }

    // source
    str highlighted = highlight2html(t.form);
    int indent = t.form.src.begin.column;
    str spaces = ("" | it + " " | int _ <- [0..indent] );

    //println("`<highlighted>`");
    HTMLElement src = readHTMLString(highlighted);
    //iprintln(src);
    HTMLElement preElt = src.elems[1].elems[0]; // parser surrounds with html/body etc.
    preElt.elems[0].elems = [text(spaces), *preElt.elems[0].elems]; // fix indentation
    elt.elems += [preElt]; 

    if (t has output) {
        elt.elems += [h4([text("Should evaluate to:")])];
        elt.elems += [pre([text("<t.output>")])];
    }

    if (t has ui) {
        elt.elems += [h4([text("Should render as:")])];
        list[HTMLElement] lst = [];
        for (Question q <- t.ui.widgets) {
            lst += [li([code([text("<q>")])],style="list-style-type: none;")];
        }
        elt.elems += [ul(lst)];
    }

    if (msgs != {}) {
        list[HTMLElement] lst = [];
        for (error(str txt, loc l) <- msgs) {
            lst += li([text("error: <txt> at line <l.begin.line - t.form.src.begin.line>")]);
        }
        elt.elems += [h4([text("Errors:")]), ul(lst)];
    }

    return elt;
}

map[str, int] addDists(map[str, int] d1, map[str, int] d2) {
    for (str k <- d2) {
        d1[k] = (d1[k]?0) + d2[k];
    }
    return d1;
}

set[Message] runTests(start[Tests] tests) {
    set[Message] msgs = {};
    
    list[HTMLElement] divs = [];

    map[str, int] coverage = ( x: 0 |  /prod(label(str x, _), _, _) := (#Form).definitions );

    for (Section section <- tests.top.sections) {
        divs += [h2([text("<section.title>"[1..-1])])];
        for (Test t <- section.tests) {
            Spec spec = extractSpec(t);
            coverage = addDists(coverage, spec.dist);
            set[Message] tmsgs = runTest(t, spec);
            divs += [testResult2HTML(t, tmsgs)];
            if (tmsgs != {}) {
                msgs += tmsgs;
            }
            else {
                msgs += {info("success", t.name.src)};
            }
        }
    }

    HTMLElement report = html([
      lang::html::AST::head([
        meta(name="viewport",content="width=device-width, initial-scale=1.0"),
        link(\rel="stylesheet", href="https://cdn.simplecss.org/simple.min.css"),
        title([text(tests.src.file)])
      ]),
      body(divs)
    ]);

    writeHTMLFile(tests.src[extension="html"], report, charset="UTF-16", escapeMode=extendedMode());

    writeFile(tests.src.top[extension="cov"], coverage);
    return msgs;
}