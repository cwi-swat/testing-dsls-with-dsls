
# Testing DSLs with DSLs

In this workshop we will introduce techniques for testing Domain-Specific Languages (DSLs): little languages dedicated to a particular problem domain.
We will introduce the aspects of a DSL that you might want to test, and strategies to automate such tests.
The workshop demonstrates these topics in the context of the [Rascal Language Workbench](https://www.rascal-mpl.org/).

Overview of the workshop:
- 60 minutes: introduction of Rascal, QL, and TestQL (a DSL for testing QL)
- 30 minutes: installation, setup, and start of exercises
- break
- 45 minutes: continue with exercises
- 45 minutes: introduce scriptless testing with [Testar](www.testar.org) and how DSL invariants can feed domain-aware oracles into Testar.

The exercises (see below) are meant to experience what it can look like to test aspects of DSLs, including the syntax, the type checker, and the dynamic semantics. The implementation in this project has bugs! So the goal is to find them by writing tests. Optionally, you can have a look at the Rascal source code of the various parts (the syntax definition, the evaluator, or the type checker) to see if you can spot them, and, even more optionally, try to fix them (in that case, please rerun the `main();` command in the terminal described below). 

### Preliminaries for the practical part

Please install [VS Code](https://code.visualstudio.com/) and then the [Rascal VS Code extension](https://marketplace.visualstudio.com/items?itemName=usethesource.rascalmpl) and the [Python extension for VS](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (you can also find these in the extension browser).

Git clone [this](https://github.com/cwi-swat/testing-dsls-with-dsls) repository (_NB: don't rename the folder!_). Finally, go to the File menu of VS Code and select "Add Folder to workspace", navigate to where you've cloned the repo, and select that directory. 

The workshop project comes with pre-wired IDE support for the Questionnaire Language (QL). 
To enable this: open the file `IDE.rsc`, and press the link at the top of the file "Import in new Rascal Terminal".
Then issue the following command in the terminal: `main();` (followed by enter).

## QL: a DSL for Questionnaires

The workshop is based on a DSL for questionnaires, called QL. A QL program consists of a form, containing questions. A question can be a normal question, that expects an answer (i.e. is answerable), or a computed question. A computed question has an associated expression which defines its value. 

Both kinds of questions have a prompt (to show to the user), an identifier (its name), and a type. The language supports boolean, integer and string types.

Questions can be conditional and the conditional construct comes in two variants: **if** and **if-else**. A block construct using `{}` can be used to group questions.

Questions are enabled and disabled when different values are entered, depending on their conditional context.

Here’s a simple questionnaire in QL from the domain of tax filing:
```
form "Tax office example" { 
  "Did you sell a house in 2010?" // the prompt of the question
    hasSoldHouse: boolean         // and its name and type
  "Did you buy a house in 2010?"
    hasBoughtHouse: boolean
  "Did you enter a loan?"
    hasMaintLoan: boolean
    
  if (hasSoldHouse) { // conditional block
    "What was the selling price?"
      sellingPrice: integer
    "Private debts for the sold house:"
      privateDebt: integer
    "Value residue:"
      valueResidue: integer =      // a computed question
        sellingPrice - privateDebt // has an expression 
  }
}
```

A full type checker of QL detects:
- references to undefined questions
- duplicate question declarations with different types
- conditions that are not of the type boolean
- operands of invalid type to operators
- duplicate labels (warning)
- cyclic data and control dependencies

Different data types in QL map to different (default) GUI widgets. For instance, boolean would be represented as checkboxes, integers as text fields with numeric sliders, and strings as text fields. The HTML form corresponding to the QP program from above will look as follows in Chrome:

<img src="https://github.com/cwi-swat/testing-dsls-with-dsls/blob/main/examples/tax.png" alt="Screenshot of the tax form" width="280" height="400" />

See the folder `examples/` for example QL programs. Opening a QL file will show links at the top for compiling, running, and testing QL programs. 
Running a questionnaire immediately opens a browser pane in VS Code. Compiling will result in an HTML file and Javascript file; opening
them in a browser will again execute the questionnaire (albeit with a slightly different layout).

If you have a recent version of the [Chrome Driver](https://googlechromelabs.github.io/chrome-for-testing/) installed (in the PATH) you can run a mini implementation of the [Testar](www.testar.org) tool to randomly test a questionnaire in Chrome by pressing the link "Run Testar". To save the domain-aware oracles, there is a link "Save oracles" to save the oracles (as Python code) that are used by Testar to evaluate each state. 


## TestQL: a DSL for testing the QL DSL

TestQL is DSL for testing QL. In fact, it's an extension of the QL language using Rascal's support for extensible syntax definition. Using TestQL, tests can be expressed in a human readable, declarative format. 

TestQL files end with the extension `testql`, and have IDE support enabled, just like the QL programs written in files with the `myql`extension. For the test files the IDE support is:

- at the top, to execute the whole test suite of show the coverage (i-e- how much of the syntax of the DSL has been covered by tests. )
- at each test case, to run an individual test.

You can find different types of tests in the file that are divided into different sections.

### Static checking tests

These tests are written using the `test ... <form>` notation, with embedded markers `$error` or `$warning` around expressions or questions. For example in the file you will find:

- a test to check that the type checker issues a error when the condition of if-then is not boolean:
```
test "condition must be boolean" 
    form "" {
        if($error(1)) {
            "X" x: integer
        }
    }
```
- test that the type checker issues a warning when the same label occurs with two questions with different names:
```
test "duplicate labels" 
    form "" {
        "same" x: integer
        $warning("same" y: boolean)
    }
```

- test that adding integers and booleans is rejected by the type checker
```
test "invalid operand to +" 
    form "" {
        "X" x: integer = $error(true) + 1
    }
```

### Dynamic semantics tests

These tests are written using the `test ... with ... <form> = {...}` format. 

- test that subtraction is left associative
```
test "subtraction associates to the left"
    with
    form "" {
        "X" x: integer = 1 - 2 - 3
    }
    = {x: -4}
```

- test that `*` has higher precedence than `+`
```
test "multiplication has higher precedence than addition"
    with
    form "" {
        "X" x: integer = 1 + 2 * 3
    }
    = {x: 7}
```

- test that disabled (invisible) questions are not changed even if given input
```
test "disabled questions are not changed"
    with x: 10
    form "" {
        if (1 > 2) "x" x: integer
    }
    = {x: 0}
```

### Rendering tests

These tests are written using the `test ... with ... <form> renders as` format. For example:
```
test "disabled questions don't render"
    with
    form "" {
        if (1 > 2) {
            "X" x: integer
        }
    }
    renders as [
    ]
```


## Exercises

Look at all the tests in `myql.testql` for inspiration. The goal of this exercise is to understand the tests and add your own tests in `yourtests.testql`. 



## Scriptless testing with domain-aware oracles for the generated webApps

Scriptless testing tools like [Testar](www.testar.org) automatically generate test sequences at the GUI level of applications. These test sequences consist of (state, action)-pairs and are generated on-the-fly by starting up the System Under Test (SUT) in its initial state (`start_SUT_and_get_driver`) and continuously selecting an action to bring the SUT into another state that is checked by oracles for failures. The Testar loop consists of:

- Deriving the set of actions that a potential user can execute in that specific state (`derive_actions`).
- Selecting one of these actions (`select_action`).
- Executing the action (`execute_action`).
- Evaluating the new state using the oracles to find failures (`check_oracles`).

You can find an implementation of a miniTestar in the file `src/testar/miniTESTAR.py`. This simplified version of Testar is capable of randomly testing the webApps that are compiled from QL programs and uses the Chrome WebDriver to get the state of the SUT.

Scriptless testing tools usually rely on generic oracles like crashes, hangs or suspicious titles. SUT-specific oracles can be added manually, however, this takes effort and can be error-prone. By encoding domain knowledge into the oracles, the scriptless tests become more a context-aware and effective way to evaluate the correctness of the generated applications.

For a QL program, e.g. `tax.myql` in the folder `examples/`, domain-aware oracles can be saved using the link "Save oracles" at the top of the editor when editing a QL program. This will save the oracles (as Python code) in a file `tax.py`, these oracles are used by miniTestar to evaluate each state in `check_oracles`.

If you have a recent version of the [Chrome Driver](https://googlechromelabs.github.io/chrome-for-testing/) installed (in the PATH) you can run a mini implementation of the [Testar](www.testar.org) tool to randomly test a questionnaire in Chrome by pressing the link "Run Testar". 

