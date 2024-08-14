module Tanja

import Message;
import IO;
import ParseTree;
import Set;

extend Syntax;

syntax Type = "*unknown*";

alias TEnv = map[str, Type];

// build a Type Environment (TEnv) for a questionnaire.
TEnv collect(start[Form] f) 
  = ( "<x>": t | /(Question)`<Str _> <Id x>: <Type t>` := f )
  + ( "<x>": t | /(Question)`<Str _> <Id x>: <Type t> = <Expr _>` := f );


/*
 * typeOf: compute the type of expressions
 */

// the fall back type is *unknown*
default Type typeOf(Expr _, TEnv env) = (Type)`*unknown*`;

// a reference has the type of its declaration
Type typeOf((Expr)`<Id x>`, TEnv env) = env["<x>"]
    when "<x>" in env;

Type typeOf((Expr)`<Expr e1> + <Expr e2>`, TEnv env) = (Type)`integer`
    when ((Type)`integer` := typeOf(e1, env)), ((Type)`integer` := typeOf(e2, env));

//ASSIGNMENT add a few more (or all) cases for typeOf.
Type typeOf((Expr)`<Expr e1> - <Expr e2>`, TEnv env) = (Type)`integer`
    when ((Type)`integer` := typeOf(e1, env)), ((Type)`integer` := typeOf(e2, env));

Type typeOf((Expr)`<Expr e1> * <Expr e2>`, TEnv env) = (Type)`integer`
    when ((Type)`integer` := typeOf(e1, env)), ((Type)`integer` := typeOf(e2, env));

Type typeOf((Expr)`<Expr e1> / <Expr e2>`, TEnv env) = (Type)`integer`
     when ((Type)`integer` := typeOf(e1, env)), ((Type)`integer` := typeOf(e2, env));

Type typeOf((Expr)`<Expr _> \< <Expr _>`, TEnv env) = (Type)`boolean`;

Type typeOf((Expr)`<Expr _> \> <Expr _>`, TEnv env) = (Type)`boolean`;

Type typeOf((Expr)`(<Expr e>)`, TEnv env) = typeOf(e, env);
Type typeOf((Expr)`<Int x>`, TEnv env) = (Type)`integer`;
Type typeOf((Expr)`<Str x>`, TEnv env) = (Type)`string`;
Type typeOf((Expr)`<Bool b>`, TEnv env) = (Type)`boolean`;
Type typeOf((Expr)`!<Expr e>`, TEnv env) = (Type)`boolean`;

//test it
test bool typeOfAdd1() = (Type)`integer` := typeOf((Expr)`1 + 2`, ());
test bool typeOfAdd2() = (Type)`integer` := typeOf((Expr)`x + 2`, ("x": (Type)`integer`));
test bool typeOfAdd3() = (Type)`integer` := typeOf((Expr)`x + y`, ("x": (Type)`integer`, "y": (Type)`integer`));
test bool typeOfSub1() = (Type)`integer` := typeOf((Expr)`1 - 2`, ());
test bool typeOfSub2() = (Type)`integer` := typeOf((Expr)`x - 2`, ("x": (Type)`integer`));
test bool typeOfSub3() = (Type)`integer` := typeOf((Expr)`x - y`, ("x": (Type)`integer`, "y": (Type)`integer`));


/*
 * Checking forms
 */

set[Message] check(start[Form] form)
  = { *check(q, env) | Question q <- form.top.questions }
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
// for if-then, if-then-else, the expression should have type boolean
// block? welke is dat?

set[Message] check((Question)`if ( <Expr e> ) { <Question* questions> }`, TEnv env)
    = { error("expected boolean", e.src) | (Type)`boolean` !:= typeOf(e, env) }
    + union({check(q, env) | q <- questions }) + check(e, env);

set[Message] check((Question)`if ( <Expr e> ) { <Question* questionsT> } else { <Question* questionsF> }`, TEnv env)
    = { error("expected boolean", e.src) | (Type)`boolean` !:= typeOf(e, env) }
    + union({check(q, env) | q <- questionsT } + {check(q, env) | q <- questionsF} );


/*
 * Checking expressions
 */


// when the other cases fail, there are no errors
default set[Message] check(Expr _, TEnv env) = {};

set[Message] check(e:(Expr)`<Id x>`, TEnv env) = {error("undefined question", x.src)}
    when "<x>" notin env;

set[Message] check((Expr)`(<Expr e>)`, TEnv env) = check(e, env);

// ASSIGNMENT, add a couple of more cases to define type checking 
// think about the different type signature of arithmetic
// comparisons (<, >, ==, etc.), and booleans (&&, etc.)


set[Message] check(e:(Expr)`<Expr x> + <Expr y>`, TEnv env)
    = { error("invalid types for addition", e.src) | 
        (Type)`integer` !:= typeOf(x, env) || (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);

set[Message] check(e:(Expr)`<Expr x> * <Expr y>`, TEnv env)
    = { error("invalid types for multiplication", e.src) | 
        (Type)`integer` !:= typeOf(x, env) || (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);

set[Message] check(e:(Expr)`<Expr x> - <Expr y>`, TEnv env)
    = { error("invalid types for substraction", e.src) | 
        (Type)`integer` !:= typeOf(x, env) || (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);

set[Message] check(e:(Expr)`<Expr x> \> <Expr y>`, TEnv env)
    = { error("invalid types for comparing", e.src) | 
        (Type)`integer` !:= typeOf(x, env) || (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);

set[Message] check(e:(Expr)`<Expr x> \< <Expr y>`, TEnv env)
    = { error("invalid types for comparing", e.src) | 
        (Type)`integer` !:= typeOf(x, env) || (Type)`integer` !:= typeOf(y, env) }
    + check(x, env) + check(y, env);


set[Message] check(e:(Expr)`! <Expr x>`, TEnv env)
    = { error("invalid type for not", x.src) | (Type)`boolean` !:= typeOf(x, env) };



void printTEnv(TEnv tenv) {
    for (str x <- tenv) {
        println("<x>: <tenv[x]>");
    }
}

void checkSnippets() {
    start[Form] pt = parse(#start[Form], |project://rascal-dsl-crashcourse/examples/tax.myql|);
    check(pt);
}


&T<:Tree myTreeAt(type[&T<:Tree] typ, Tree root, loc l) {
    visit (root) {
        case &T<:Tree t: {
            if (t.src == l) {
                return t;
            }
        }
    }
    throw "not found";
}

test bool testIfThen1() = {error("expected boolean", loc l)} := check(q, ()) && treeFound((Expr)`1`) := treeAt(#Expr, l, q)
  when Question q := (Question)`if (1) {}`;
test bool testIfThen2() = {} := check(q, ())
  when Question q := (Question)`if (true) {}`;
test bool testIfThen3() = {error("expected boolean", loc l)} := check(q, ()) && (Expr)`2` := myTreeAt(#Expr, q, l)
  when Question q := (Question)`if (true) {if (2) {}}`;


test bool testIfThen4() = {error("expected boolean", _)} := check(q, ())
  when Question q := (Question)`if (true) {if (2) {}}`;


test bool testIfThen5() = {error("invalid type for not", loc l)} := check(q, ()) //&& treeFound((Expr)`2`) := treeAt(#Expr, l, q)
  when Question q := (Question)`if (!6) {}`;
test bool testIfThen6() = {} := check(q, ())
  when Question q := (Question)`if (!true) {}`;

test bool testIfThenElse1() = {error("expected boolean", loc l)} := check(q, ()) && treeFound((Expr)`1`) := treeAt(#Expr, l, q)
  when Question q := (Question)`if (1) {} else {}`;
test bool testIfThenElse2() = {} := check(q, ())
  when Question q := (Question)`if (false) {} else {}`;


test bool testTax() = {} := check(parse(#start[Form], |project://rascal-dsl-crashcourse/examples/tax.myql|));
test bool testErrors() = {error("invalid types for multiplication",_), error("incompatible type", _), error("undefined question", _), error("invalid types for substraction",_), error(
    "expected boolean",_)} := check(parse(#start[Form], |project://rascal-dsl-crashcourse/examples/errors.myql|));
test bool testEmpty() = {} := check(parse(#start[Form], |project://rascal-dsl-crashcourse/examples/empty.myql|));
test bool testCyclic() = {} := check(parse(#start[Form], |project://rascal-dsl-crashcourse/examples/cyclic.myql|));
test bool testBinary() = {} := check(parse(#start[Form], |project://rascal-dsl-crashcourse/examples/binary.myql|));