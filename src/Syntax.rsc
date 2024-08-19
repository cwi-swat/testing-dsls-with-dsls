module Syntax

extend lang::std::Layout;
extend lang::std::Id;

import ParseTree;
import vis::Text;
import IO;

// TIP: see bottom of this file for snippets to be pasted into the terminal.


syntax Name = Id; // because redef/extend of Id from standard lib does not work. 

// syntax of a questionnaire
start syntax Form 
  = "form" Str title "{" Question* questions "}"; 

// Here's a simple syntax of String literals
lexical Str = [\"]![\"]* [\"];

// ASSIGNMENT: define the syntax of boolean literals.
lexical Bool = "true" | "false";

// ASSIGNMENT define the syntax of integer literals
// Docs: https://www.rascal-mpl.org/docs/Rascal/Declarations/SyntaxDefinition/Symbol/
lexical Int = [\-]?[0-9]+;

// ASSIGNMENT: define the syntax of type keywords  
syntax Type = "integer" | "boolean" | "string";



// ASSIGNMENT: complete the syntax of Questions
// add normal questions, computed question, block of questions, and if-then-else
// look at the examples directory for how such questions should look. 
// Docs: https://www.rascal-mpl.org/docs/Rascal/Declarations/SyntaxDefinition/
syntax Question 
  = ifThen: "if" "(" Expr cond ")" Question then () !>> "else" 
  | ifThenElse: "if" "(" Expr cond ")" Question then "else" Question else
  | block: "{" Question* questions "}"
  | answerable: Str prompt Name name ":" Type type
  | computed: Str prompt Name name ":" Type type "=" Expr expr
  ;



// ASSIGNMENT: complete the expression grammar with expressions for
// +, -, <, <=, >, >=, ==, !=, &&, ||
// (note that in literals you have to escape < and >, like \< and \> respectively)
// observe how > is used in the grammar to declare operator precedence 
// similar for the keyword "left" (or right, or non-assoc) for associativity.
// hint: https://www.rascal-mpl.org/docs/Rascal/Declarations/SyntaxDefinition/Disambiguation/
syntax Expr
  = var: Name name \ "true" \"false"
  | integer: Int
  | string: Str
  | boolean: Bool
  | bracket "(" Expr ")"
  | not: "!" Expr
  > left (
      Expr "*" Expr
    | Expr "/" Expr
  )
  > left (
      Expr "+" Expr
    | Expr "-" Expr
  )
  > non-assoc (
      Expr "==" Expr
    | Expr "!=" Expr
    | Expr "\>" Expr
    | Expr "\<" Expr
    | Expr "\<=" Expr
    | Expr "\>=" Expr
  )
  > left Expr "&&" Expr
  > left Expr "||" Expr
  ;

void snippets() {
  // to enable IDE support: 
  //    import IDE;
  //    main();
  // now you can double click on files in the examples folder.


  // first do: 
  //   import ParseTree; 
  //   import Syntax;
  start[Form] pt = parse(#start[Form], |project://rascal-dsl-crashcourse/examples/tax.myql|);

  // import IO;
  // import vis::Text;
  println(prettyTree(pt)); // inspect the parse tree
  println(prettyTree(pt,src=true)); // ctrl-/cmd-click on source locations

  // if you get an ambiguity error, try:
  pt = parse(#start[Form], |project://rascal-dsl-crashcourse/examples/tax.myql|, allowAmbiguity=true);
  // then inspect (amb nodes are indicated with diamonds):
  println(prettyTree(pt));

  // you can also parse smaller snippets of code:
  Expr expr = parse(#Expr, "a + b");
  println(prettyTree(expr));

}

