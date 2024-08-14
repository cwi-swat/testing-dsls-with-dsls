module App

import salix::HTML;
import salix::App;
import salix::Core;
import salix::Index;

import Eval;
import Syntax;

import String;
import ParseTree;

// The salix application model is a tuple
// containing the questionnaire and its current run-time state (env).
alias Model = tuple[start[Form] form, VEnv env];

App[Model] runQL(start[Form] ql) = webApp(qlApp(ql), |project://rascal-dsl-crashcourse/src/main/rascal|);

SalixApp[Model] qlApp(start[Form] ql, str id="root") 
  = makeApp(id, 
        Model() { return <ql, initialEnv(ql)>; }, 
        withIndex("<ql.top.name>", id, view, css=["https://cdn.simplecss.org/simple.min.css"]), 
        update);


// The salix Msg type defines the application events.
data Msg
  = updateInt(str name, str n)
  | updateBool(str name, bool b)
  | updateStr(str name, str s)
  ;

// We map messages to Input values 
// to be able to reuse the interpreter defined in Eval.
Input msg2input(updateInt(str q, str n)) = user(q, vint(toInt(n)));
Input msg2input(updateBool(str q, bool b)) = user(q, vbool(b));
Input msg2input(updateStr(str q, str s)) = user(q, vstr(s));

// The Salix model update function simply evaluates the user input
// to obtain the new state. 
Model update(Msg msg, Model model) = model[env=eval(model.form, msg2input(msg), model.env)];

// Salix view rendering works by "drawing" on an implicit HTML canvas.
// Note how html elements are drawn, and how element nesting is achieved with
// nesting of void-closures.
void view(Model model) {
    h3(model.form.top.name);
    form(() {
        table(() {
            tbody(() {
                for (Question q <- model.form.top.questions) {
                    viewQuestion(q, model);
                }
            });
        });
    });
}

// ASSIGNMENT: complete rendering of questions for
// if-then, if-then-else, block, and computed questions.
// to evaluate conditions call eval, and pass in model.env
// for the latter take inspiration from the normal question rendering
// and use the attribute disabeld(true) to make them read only. 
void viewQuestion(Question q, Model model) {

    switch (q) {
        case (Question)`<Str s> <Id x>: <Type t>`: {
            tr(() {
                td(() {
                    label("<s>");
                });

                td(() {
                    switch (<t, model.env["<x>"]>) {
                        case <(Type)`integer`, vint(int i)>:
                            input(\type("number"), \value("<i>"), onChange(partial(updateInt, "<x>")));
                        case <(Type)`boolean`, vbool(bool b)>:
                            input(\type("checkbox"),checked(b), onClick(updateBool("<x>", !b)));
                        case <(Type)`string`, vstr(str s)>:
                            input(\type("text"), \value("<s>"), onChange(partial(updateStr, "<x>")));
                    }
                });
            });
        }

        case (Question)`<Str s> <Id x>: <Type t> = <Expr _>`: {
            tr(() {
                td(() {
                    label("<s>");
                });

                td(() {
                    switch (<t, model.env["<x>"]>) {
                        case <(Type)`integer`, vint(int i)>:
                            input(\type("number"), \value("<i>"), disabled(true));
                        case <(Type)`boolean`, vbool(bool b)>:
                            input(\type("checkbox"),checked(b), disabled(true));
                    }    
                });   
            });
        }

        default: throw "unknown question type";

    }
}

void appSnippets() {
    start[Form] pt = parse(#start[Form], |project://rascal-dsl-crashcourse/examples/tax.myql|);
    runQL(pt);
}
