module Compile
import Syntax;
// if you want to make a compiler to html, use:
import lang::html::AST; // modeling HTML docs
import lang::html::IO; // reading/writing HTML

// and use string templates to generate JS:
str stringTemplates() {
    // e.g.
    return "function bla() {
           '  <for (Question q <- form.top.questions) {>
           '     <q2js(q)>
           '  <}>
           '}";
}

// use source locations to provide unique ids to HTML elements.
// use JS code to CSS visible:false/true the elements if conditions are false.

// Another tip: normalize QL first:
list[Question] flatten(start[Form] form) 
  = [ *flatten(q, (Expr)`true`) | Question q <- form.top.questions ];

list[Question] flatten((Question)`{<Question* qs>}`, Expr cond)
  = [ *flatten(q, cond) | Question q <- qs ];

list[Question] flatten((Question)`if (<Expr e>) <Question q>`, Expr cond)
  = flatten(q, (Expr)`<Expr cond> && <Expr e>`);

default list[Question] flatten(Question q, Expr cond)
  = [(Question)`if (<Expr cond>)
               '  <Question q>`];

