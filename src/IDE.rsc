module IDE

/*
 * Import this module in a Rascal terminal and execute `main()`
 * to enable language services in the IDE.
 */

import util::LanguageServer;
import util::Reflective;
import util::IDEServices;

import Syntax;
import Check;
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
    lenses(testLenses),
    executor(testCommands)
};

data Command
  = runTestSuite(start[Tests] tests);

Summary mySummarizer(loc origin, start[Form] input) {
  return summary(origin, messages = {<m.at, m> | Message m <- check(input) });
}

data Command
  = runQuestionnaire(start[Form] form);

rel[loc,Command] myLenses(start[Form] input) = {<input@\loc, runQuestionnaire(input, title="Run...")>};


rel[loc,Command] testLenses(start[Tests] input) = {<input@\loc, runTestSuite(input, title="Run tests (<countTests(input.top)>)")>};

int countTests(Tests tests) = ( 0 | it + 1 | Test t <- tests.tests );

void myCommands(runQuestionnaire(start[Form] form)) {
    showInteractiveContent(runQL(form));
}

void testCommands(runTestSuite(start[Tests] tests)) {
    set[Message] msgs = runTests(tests);
    //unregisterDiagnostics(LOCS);
    registerDiagnostics([ m | Message m <- msgs]);
    //LOCS = [ m.at | Message m <- msgs ];
}


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


