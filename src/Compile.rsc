module Compile

import Syntax;
import Eval;
import IO;
import ParseTree;


import lang::html::AST; // modeling HTML docs
import lang::html::IO; // reading/writing HTML


void compile(start[Form] form) {
  loc h = form.src[extension="html"];
  loc j = form.src[extension="js"].top;
  <js, ht> = compile2jsHtml(form, j);
  writeFile(j, js);
  writeHTMLFile(h, ht, escapeMode=extendedMode());
}

tuple[str, HTMLElement] compile2jsHtml(start[Form] form, loc j) {
  list[Question] qs = flatten(form);
  str js = "<init2js(form)>\n<update2js(qs)>\n";
  HTMLElement ht = questions2html("<form.top.title>"[1..-1], qs, j.file);
  return <js, ht>;
}

str init2js(start[Form] form) {
  VEnv env = initialEnv(form);

  return "var $state = {
         '  <for (str x <- env) {>
         '  <x>: <value2js(env[x])>,
         '  <}>
         '}";
}

str value2js(vint(int n)) = "<n>";
str value2js(vstr(str s)) = "\"<s>\"";
str value2js(vbool(bool b)) = "<b>";



HTMLElement questions2html(str name, list[Question] qs, str jsFile) 
  = html([
      lang::html::AST::head([
        link(\rel="stylesheet", href="https://cdn.simplecss.org/simple.min.css"),
        script([], src=jsFile),
        script([text("document.addEventListener(\"DOMContentLoaded\", function() {
                     '  $update();
                     '});")]), 
        title([text(name)])
      ]),
      body([
        h2([text(name)]),
        *[ question2html(q) | (Question)`if (<Expr _>) <Question q>` <- qs ]
      ])
  ]);

HTMLElement question2html(q:(Question)`<Str l> <Id x>: <Type t>`)
  = div([
      label([text("<l>"[1..-1])]),
      type2widget(q, t, false)
    ],id=divId(q));

HTMLElement question2html(q:(Question)`<Str l> <Id x>: <Type t> = <Expr _>`)
  = div([
      label([text("<l>"[1..-1])]),
      type2widget(q, t, true)
    ],id=divId(q));


str widgetId(Question q) = "<q.name>_widget_<q.src.offset>";

str divId(Question q) = "<q.name>_div_<q.src.offset>";

HTMLElement type2widget(Question q, (Type)`boolean`, bool disabled)
  = disabled 
  ? input(\type="checkbox", id=widgetId(q), disabled="true")
  : input(\type="checkbox", id=widgetId(q), onclick="$update(\'<q.name>\', event.target.checked);");

HTMLElement type2widget(Question q, (Type)`integer`, bool disabled)
  = disabled 
   ? input(\type="number", id=widgetId(q), disabled="true")
   : input(\type="number", id=widgetId(q), 
      onchange="$update(\'<q.name>\', Math.floor(Number(event.target.value)));");

HTMLElement type2widget(Question q, (Type)`string`, bool disabled)
  = disabled 
  ? input(\type="text", id=widgetId(q), disabled="true")
  : input(\type="text", id=widgetId(q), onchange="$update(\'<q.name>\', event.target.value);");


str update2js(list[Question] form) {
  return "function $update(name, value) {
         '   let change = \'\';
         '   let newVal = undefined;
         '   let div = undefined;
         '   if (name !== undefined) {
         '      $state[name] = value;
         '   }
         '   else {
         '     let elt = null;
         '     let div = null;
         '   <for ((Question)`if (<Expr c>) <Question q>` <- form) {>
         '     elt = document.getElementById(\'<widgetId(q)>\');
         '     <if ((Type)`boolean` := q.\type) {>
         '     elt.checked = $state.<q.name>;
         '     <} else {>
         '     elt.value = $state.<q.name>;
         '     <}>
         '     div = document.getElementById(\'<divId(q)>\');
         '     div.style.display = <expr2js(c)> ? \'block\' : \'none\'; 
         '   <}>
         '     return;
         '   }
         '   do {
         '     change = \'\';
         '     <for ((Question)`if (<Expr c>) <Question q>` <- form) {>
         '     div = document.getElementById(\'<divId(q)>\');
         '     div.style.display = <expr2js(c)> ? \'block\' : \'none\'; 
         '     <if (q has expr) {>
         '     if (<expr2js(c)>) {
         '        if (change === \'<q.name>\') {
         '           console.log(\'ERROR: mutual exclusion bug on <q.name>\');
         '           break;
         '        }
         '        newVal = <expr2js(q.expr)>;
         '        if (newVal !== $state.<q.name>) {
         '          let elt = document.getElementById(\'<widgetId(q)>\');
         '          $state.<q.name> = newVal;
         '          <if ((Type)`boolean` := q.\type) {>
         '          elt.checked = newVal;
         '          <} else {>
         '          elt.value = newVal;
         '          <}>
         '         change = \'<q.name>\';
         '       }
         '     }
         '     <}>
         '     <}>
         '   } while (change !== \'\');
         '}";

}

str expr2js((Expr)`<Id x>`) = "$state.<x>"; 
str expr2js((Expr)`<Int x>`) = "<x>";
str expr2js((Expr)`<Bool x>`) = "<x>";
str expr2js((Expr)`<Str x>`) = "<x>";
str expr2js((Expr)`(<Expr x>)`) = "(<expr2js(x)>)";
str expr2js((Expr)`!<Expr x>`) = "!(<expr2js(x)>)";
str expr2js((Expr)`<Expr x> + <Expr y>`) = "(<expr2js(x)> + <expr2js(y)>)";
str expr2js((Expr)`<Expr x> - <Expr y>`) = "(<expr2js(x)> - <expr2js(y)>)";
str expr2js((Expr)`<Expr x> * <Expr y>`) = "(<expr2js(x)> * <expr2js(y)>)";
str expr2js((Expr)`<Expr x> / <Expr y>`) 
  = "(function () { const div = <expr2js(y)>; return div !== 0 ? Math.ceil(<expr2js(x)> / div) : 0; })()";


str expr2js((Expr)`<Expr x> == <Expr y>`) = "(<expr2js(x)> === <expr2js(y)>)";
str expr2js((Expr)`<Expr x> != <Expr y>`) = "(<expr2js(x)> !== <expr2js(y)>)";
str expr2js((Expr)`<Expr x> \> <Expr y>`) = "(<expr2js(x)> \> <expr2js(y)>)";
str expr2js((Expr)`<Expr x> \>= <Expr y>`) = "(<expr2js(x)> \>= <expr2js(y)>)";
str expr2js((Expr)`<Expr x> \< <Expr y>`) = "(<expr2js(x)> \< <expr2js(y)>)";
str expr2js((Expr)`<Expr x> \<= <Expr y>`) = "(<expr2js(x)> \<= <expr2js(y)>)";
str expr2js((Expr)`<Expr x> && <Expr y>`) = "(<expr2js(x)> && <expr2js(y)>)";
str expr2js((Expr)`<Expr x> || <Expr y>`) = "(<expr2js(x)> || <expr2js(y)>)";


list[Question] flatten(start[Form] form) 
  = [ *flatten(q, (Expr)`true`) | Question q <- form.top.questions ];

list[Question] flatten((Question)`{<Question* qs>}`, Expr cond)
  = [ *flatten(q, cond) | Question q <- qs ];

list[Question] flatten((Question)`if (<Expr e>) <Question q>`, Expr cond)
  = flatten(q, (Expr)`<Expr cond> && <Expr e>`);

list[Question] flatten((Question)`if (<Expr e>) <Question q> else <Question els>`, Expr cond)
  = flatten(q, (Expr)`<Expr cond> && <Expr e>`)
  + flatten(els, (Expr)`<Expr cond> && !(<Expr e>)`);

default list[Question] flatten(Question q, Expr cond)
  = [(Question)`if (<Expr cond>) <Question q>`];

