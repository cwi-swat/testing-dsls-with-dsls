module GenScript

import Syntax;
import Eval;
import util::Math;
import String;
import List;

import Compile;
import ParseTree;

/*
state S0
derive enabled questions
select one of them (random), fill in with a random value
  but not one you’ve already selected
  if such is not available, pick one earlier selected, but different value

update state
repeat

*/

alias Script = lrel[Input action, VEnv state, set[str] visible];

Script genScript(start[Form] form, int length=10) {
    VEnv venv = initialEnv(form);
    set[str] seen = {};
    return for (int _ <- [0..length]) {
        list[Question] candidates = [ q | Question q <- render(form, venv), !(q has expr) ];
        list[Question] unseenCandidates = [ q | Question q <- candidates, "<q.name>" notin seen ];
        if (unseenCandidates == []) {
            // start over
            unseenCandidates = candidates;
            seen = {};
        }

        if (unseenCandidates != []) {
            int i = arbInt(size(unseenCandidates));
            Question focus = unseenCandidates[i];
            seen += {"<focus.name>"};
            Input inp = user("<focus.name>", arbValue(focus.\type));
            venv = eval(form, inp, venv);
            // we need to render again, because venv has changed
            // and we need to include computed questions 
            set[str] visible = { "<q.name>" | Question q <- render(form, venv) };
            append <inp, venv, visible>;
        }
    }
}

Value arbValue((Type)`integer`) = vint(arbInt(5000));
Value arbValue((Type)`boolean`) = vbool(arbInt(2) == 1);
Value arbValue((Type)`string`) = vstr(arbString(arbInt(100)));

list[str] genAsserts(start[Form] form) {
    list[Question] qs = flatten(form);

    asserts = for ((Question)`if (<Expr cond>) <Question q>` <- qs) {
        append "assert not <expr2py(cond)> or driver.find_elements(By.ID, \'<divId(q)>\')[0].is_displayed";
        //append "assert not <expr2py(cond)> or driver.find_elements(By.ID, \'<divId(q)>\')[0].is_enabled";
        if (q has expr) {
            append "assert state[\'<q.name>\'] == <expr2py(q.expr)>";
        }

        list[Question] others = [ q2 | (Question)`if (<Expr cond>) <Question q2>` <- qs, 
                Name x := q.name, x := q2.name, q2.src != q.src ];

        if (others != []) {
            append "if driver.find_elements(By.ID, \'<divId(q)>\')[0].is_displayed:
                   '    <for (Question q2 <- others) {>
                   '    assert not driver.find_elements(By.ID, \'<divId(q2)>\')[0].is_displayed
                   '    <}>
                   '";
        }

    }

    return asserts;
}

str genTestarOracle(start[Form] form) {
    list[str] asserts = genAsserts(form);
    str name = replaceAll(form.src.file, ".", "_");
    return "from selenium.webdriver.common.by import By
           'def <name>_oracle(driver):
           '    state = driver.execute_script(\'return $state;\');
           '    <for (str a <- asserts) {>
           '    <a><}>
           '"; 
}

str expr2py((Expr)`<Id x>`) = "state[\'<x>\']"; 
str expr2py((Expr)`<Int x>`) = "<x>";
str expr2py((Expr)`<Bool x>`) = "<x>" == "true" ? "True" : "False";
str expr2py((Expr)`<Str x>`) = "\'" + "<x>"[1..-1] + "\'";
str expr2py((Expr)`(<Expr x>)`) = "(<expr2py(x)>)";
str expr2py((Expr)`!<Expr x>`) = "not (<expr2py(x)>)";
str expr2py((Expr)`<Expr x> + <Expr y>`) = "(<expr2py(x)> + <expr2py(y)>)";
str expr2py((Expr)`<Expr x> - <Expr y>`) = "(<expr2py(x)> - <expr2py(y)>)";
str expr2py((Expr)`<Expr x> * <Expr y>`) = "(<expr2py(x)> * <expr2py(y)>)";
str expr2py((Expr)`<Expr x> / <Expr y>`) 
  = "(lambda div: (<expr2py(x)> / div) if div != 0 else 0)(<expr2py(y)>)";


str expr2py((Expr)`<Expr x> == <Expr y>`) = "(<expr2py(x)> == <expr2py(y)>)";
str expr2py((Expr)`<Expr x> != <Expr y>`) = "(<expr2py(x)> != <expr2py(y)>)";
str expr2py((Expr)`<Expr x> \> <Expr y>`) = "(<expr2py(x)> \> <expr2py(y)>)";
str expr2py((Expr)`<Expr x> \>= <Expr y>`) = "(<expr2py(x)> \>= <expr2py(y)>)";
str expr2py((Expr)`<Expr x> \< <Expr y>`) = "(<expr2py(x)> \< <expr2py(y)>)";
str expr2py((Expr)`<Expr x> \<= <Expr y>`) = "(<expr2py(x)> \<= <expr2py(y)>)";
str expr2py((Expr)`<Expr x> && <Expr y>`) = "(<expr2py(x)> and <expr2py(y)>)";
str expr2py((Expr)`<Expr x> || <Expr y>`) = "(<expr2py(x)> or <expr2py(y)>)";
