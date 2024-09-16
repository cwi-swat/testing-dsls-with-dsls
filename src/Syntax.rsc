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
  = form: "form" Str title "{" Question* questions "}"; 

lexical Str = [\"]![\"]* [\"];

lexical Bool = "true" | "false";

lexical Int = [\-]?[0-9]+;

syntax Type = integer: "integer" | boolean: "boolean" | string: "string";


syntax Question 
  = ifThen: "if" "(" Expr cond ")" Question then () !>> "else" 
  | ifThenElse: "if" "(" Expr cond ")" Question then "else" Question else
  | block: "{" Question* questions "}"
  | answerable: Str prompt Name name ":" Type type
  | computed: Str prompt Name name ":" Type type "=" Expr expr
  ;


syntax Expr
  = var: Name name \ "true" \"false"
  | integer: Int
  | string: Str
  | boolean: Bool
  | bracket "(" Expr ")"
  | not: "!" Expr
  > left (
      mul: Expr "*" Expr
    | div: Expr "/" Expr
  )
  > left (
      add: Expr "+" Expr
    | sub: Expr "-" Expr
  )
  > non-assoc (
      eq: Expr "==" Expr
    | neq: Expr "!=" Expr
    | gt: Expr "\>" Expr
    | lt: Expr "\<" Expr
    | leq: Expr "\<=" Expr
    | geq: Expr "\>=" Expr
  )
  > left and: Expr "&&" Expr
  > left or: Expr "||" Expr
  ;

