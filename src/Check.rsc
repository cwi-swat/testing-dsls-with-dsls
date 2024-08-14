module Check

import Message;
import IO;
import ParseTree;

extend Syntax;


syntax Type = "*unknown*";

//data Tree(loc src = |unknown:///|);

alias TEnv = lrel[str, Type];

// build a Type Environment (TEnv) for a questionnaire.
TEnv collect(Form f) 
  = [ <"<x>", t> | /(Question)`<Str _> <Id x>: <Type t>` := f ]
  + [ <"<x>", t> | /(Question)`<Str _> <Id x>: <Type t> = <Expr _>` := f ];


/*
 * typeOf: compute the type of expressions
 */

// the fall back type is *unknown*
default Type typeOf(Expr _, TEnv env) = (Type)`*unknown*`;

// a reference has the type of its declaration
Type typeOf((Expr)`<Id x>`, TEnv env) = t
    when <"<x>", Type t> <- env;

Type typeOf((Expr)`(<Expr e>)`, TEnv env) = typeOf(e, env);

Type typeOf((Expr)`<Int _>`, TEnv env) = (Type)`integer`;

Type typeOf((Expr)`<Bool _>`, TEnv env) = (Type)`boolean`;

Type typeOf((Expr)`<Str _>`, TEnv env) = (Type)`string`;

Type typeOf((Expr)`<Expr _> + <Expr _>`, TEnv env) = (Type)`integer`;

//ASSIGNMENT add a few more (or all) cases for typeOf.

Type typeOf((Expr)`<Expr _> * <Expr _>`, TEnv env) = (Type)`integer`;
Type typeOf((Expr)`<Expr _> / <Expr _>`, TEnv env) = (Type)`integer`;
Type typeOf((Expr)`<Expr _> - <Expr _>`, TEnv env) = (Type)`integer`;

Type typeOf((Expr)`<Expr _> \< <Expr _>`, TEnv env) = (Type)`boolean`;
Type typeOf((Expr)`<Expr _> \> <Expr _>`, TEnv env) = (Type)`boolean`;
Type typeOf((Expr)`<Expr _> \>= <Expr _>`, TEnv env) = (Type)`boolean`;
Type typeOf((Expr)`<Expr _> \<= <Expr _>`, TEnv env) = (Type)`boolean`;

/*
 * Checking forms
 */

set[Message] check(start[Form] form) = check(form.top);

set[Message] check(Form form) 
  = { *check(q, env) | Question q <- form.questions }
  when TEnv env := collect(form);


/*
 * Checking questions
 */

// by default, there are no errors
default set[Message] check(Question _, TEnv _) = {};


// a computed question must have an expression that is type 
// compatible with its declared type.
set[Message] check((Question)`<Str _> <Id x>: <Type t> = <Expr e>`, TEnv env)
    = { error("incompatible type", e.src) | t !:= typeOf(e, env) }
    + check(e, env);

// ASSIGNMENT complete the check definition by adding cases 
// for if-then, if-then-else, and block.

set[Message] check((Question)`if (<Expr cond>) <Question then>`, TEnv env)
    = { error("expected boolean", cond.src) | (Type)`boolean` !:= typeOf(cond, env) }
    + check(cond, env) + check(then, env);

set[Message] check((Question)`{<Question* qs>}`, TEnv env)
    = { *check(q, env) | Question q <- qs };


/*
 * Checking expressions
 */


// when the other cases fail, there are no errors
default set[Message] check(Expr _, TEnv env) = {};

set[Message] check(e:(Expr)`<Id x>`, TEnv env) = {error("undefined question", x.src)}
    when "<x>" notin env<0>;

set[Message] check((Expr)`(<Expr e>)`, TEnv env) = check(e, env);

// ASSIGNMENT, add a couple of more cases to define type checking 
// think about the different type signature of arithmetic
// comparisons (<, >, ==, etc.), and booleans (&&, etc.)

// BUG using the e: pattern binder, we cannot access .src 
set[Message] check((Expr)`<Expr x> + <Expr y>`, TEnv env)
    = { error("invalid operand", x.src) | (Type)`integer` !:= typeOf(x, env) }
    + { error("invalid operand", y.src) | (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);


set[Message] check(e:(Expr)`<Expr x> * <Expr y>`, TEnv env)
    = { error("invalid types for multiplication", e.src) | 
        (Type)`integer` !:= typeOf(x, env) || (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);

set[Message] check(e:(Expr)`<Expr x> - <Expr y>`, TEnv env)
    = { error("invalid types for subtraction", e.src) | 
        (Type)`integer` !:= typeOf(x, env) || (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);

set[Message] check((Expr)`<Expr x> \< <Expr y>`, TEnv env)
    = { error("invalid operand", x.src) | (Type)`integer` !:= typeOf(x, env) }
    + { error("invalid operand", y.src) | (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);

set[Message] check((Expr)`<Expr x> \> <Expr y>`, TEnv env)
    = { error("invalid operand", x.src) | (Type)`integer` !:= typeOf(x, env) }
    + { error("invalid operand", y.src) | (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);

void printTEnv(TEnv tenv) {
    for (<str x, Type t> <- tenv) {
        println("<x>: <t>");
    }
}

void checkSnippets() {
    start[Form] pt = parse(#start[Form], |project://rascal-dsl-crashcourse/examples/tax.myql|);
    check(pt);
}
 
