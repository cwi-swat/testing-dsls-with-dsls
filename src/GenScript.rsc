module GenScript

import Syntax;
import Eval;
import util::Math;
import String;
import List;


/*
state S0
derive enabled questions
select one of them (random), fill in with a random value
  but not one you’ve already selected
  if such is not available, pick one earlier selected, but different value

update state
repeat

*/

list[Input] genScript(start[Form] form, int length=10) {
    list[Input] script = [];

    VEnv venv = initialEnv(form);
    for (int i <- [0..length]) {
        list[Question] ui = render(form, venv);
        list[Question] candidates = [ q | Question q <- ui, !(q has expr) ];
        int i = arbInt(size(candidates));
        Question focus = candidates[i];
        Input inp = user("<focus.name>", arbValue(focus.\type));
        script += [inp];
        venv = eval(form, inp, venv);
    }

    return script;
}

Value arbValue((Type)`integer`) = vint(arbInt());
Value arbValue((Type)`boolean`) = vbool(arbInt(2) == 1);
Value arbValue((Type)`string`) = vstr(arbString(arbInt(100)));