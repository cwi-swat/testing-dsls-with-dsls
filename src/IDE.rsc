module IDE

/*
 * Import this module in a Rascal terminal and execute `main()`
 * to enable language services in the IDE.
 */

import util::LanguageServer;
import util::Reflective;
import util::IDEServices;
import IO;

import Syntax;
import Compile;
import Check;
import GenScript;
import App;
import Message;
import ParseTree;
import TestLang;


set[LanguageService] myLanguageContributor() = {
    parser(Tree (str input, loc src) {
        return parse(#start[Form], input, src);
    }),
    lenses(myLenses),
    executor(myCommands),
    summarizer(mySummarizer
        , providesDocumentation = false
        , providesDefinitions = false
        , providesReferences = false
        , providesImplementations = false)
};

set[LanguageService] testLanguageContributor() = {
    parser(Tree (str input, loc src) {
        return parse(#start[Tests], input, src);
    }),
    outliner(testOutliner),

    lenses(testLenses),
    executor(testCommands)
};

data Command
  = runTestSuite(start[Tests] tests)
  | runSingleTest(Test theTest);

Summary mySummarizer(loc origin, start[Form] input) {
  return summary(origin, messages = {<m.at, m> | Message m <- check(input) });
}

data Command
  = runQuestionnaire(start[Form] form)
  | compileQuestionnaire(start[Form] form)
  | saveOracle(start[Form] form)
  ;


rel[loc,Command] myLenses(start[Form] input) 
  = {<input@\loc, runQuestionnaire(input, title="Run...")>,
     <input.src, compileQuestionnaire(input, title="Compile")>,
     <input.src, saveOracle(input, title="Save oracle")>};


rel[loc,Command] testLenses(start[Tests] input) = {<input@\loc, runTestSuite(input, title="Run tests (<countTests(input)>)")>}
    + {< t.src, runSingleTest(t, title="Run this test")> | Section s <- input.top.sections, Test t <- s.tests };

int countTests(start[Tests] tests) = ( 0 | it + 1 | /Test _ := tests );

void myCommands(runQuestionnaire(start[Form] form)) {
    showInteractiveContent(runQL(form));
}

void myCommands(compileQuestionnaire(start[Form] form)) {
    compile(form);
}

void myCommands(saveOracle(start[Form] form)) {
    loc l = form.src.top[extension="py"];
    writeFile(l, genTestarOracle(form));
}

void testCommands(runTestSuite(start[Tests] tests)) {
    set[Message] msgs = runTests(tests);
    registerDiagnostics([ m | Message m <- msgs]);
}

void testCommands(runSingleTest(Test t)) {
    set[Message] msgs = runTest(t);
    registerDiagnostics([ m | Message m <- msgs]);
}

list[DocumentSymbol] testOutliner(start[Tests] input) 
  = [symbol("<s.title>"[1..-1], \module(), input.src,
        children=[ symbol("<t.name>"[1..-1], \class(), t.src) | Test t <- s.tests ])
        | Section s <- input.top.sections ];

void main() {
    registerLanguage(
        language(
            pathConfig(srcs = [|std:///|, |project://testing-dsls-with-dsls/src|]),
            "QL",
            "myql",
            "IDE",
            "myLanguageContributor"
        )
    );
    registerLanguage(
        language(
            pathConfig(srcs = [|std:///|, |project://testing-dsls-with-dsls/src|]),
            "TestLang",
            "test",
            "IDE",
            "testLanguageContributor"
        )
    );
}


