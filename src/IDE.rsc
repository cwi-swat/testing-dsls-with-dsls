module IDE

/*
 * Import this module in a Rascal terminal and execute `main()`
 * to enable language services in the IDE.
 */

import util::LanguageServer;
import util::Reflective;
import util::IDEServices;
import util::ShellExec;
import IO;
import ValueIO;
import List;
import vis::Charts;

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
  | runSingleTest(Test theTest)
  | showCoverage(start[Tests] tests);

Summary mySummarizer(loc origin, start[Form] input) {
  return summary(origin, messages = {<m.at, m> | Message m <- check(input) });
}

data Command
  = runQuestionnaire(start[Form] form)
  | compileQuestionnaire(start[Form] form)
  | saveOracle(start[Form] form)
  | runTestar(start[Form] form)
  ;


rel[loc,Command] myLenses(start[Form] input) 
  = {<input@\loc, runQuestionnaire(input, title="Run...")>,
     <input.src, compileQuestionnaire(input, title="Compile")>,
     <input.src, saveOracle(input, title="Save oracle")>,
     <input.src, runTestar(input, title="Run Testar")>};


rel[loc,Command] testLenses(start[Tests] input) 
    = {<input@\loc, runTestSuite(input, title="Run tests (<countTests(input)>)")>,
       <input@\loc, showCoverage(input, title="Show coverage")>}
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

void myCommands(runTestar(start[Form] form)) {
    loc l = form.src.top[extension="py"];
    writeFile(l, genTestarOracle(form));
    loc resolved = resolveLocation(form.src);
    <output, code> = execWithCode(|PATH:///python3|, workingDir=resolveLocation(|project://testing-dsls-with-dsls/|),
        args=["src/testar/testingQLprograms.py", resolved[extension="html"].path]);

    output += "<resolveLocation(|cwd:///|)>";
    loc out = form.src.top[extension="testar"];
    writeFile(out, output);
    edit(out);
}


void testCommands(runTestSuite(start[Tests] tests)) {
    set[Message] msgs = runTests(tests);
    registerDiagnostics([ m | Message m <- msgs]);
}

void testCommands(showCoverage(start[Tests] tests)) {
    loc covFile = tests.src.top[extension="cov"];
    if (!exists(covFile)) {
        runTests(tests);
    }
    map[str,int] covdist = readTextValueFile(#map[str,int], covFile);
    lrel[str,int] lst = [ <k, covdist[k]> | k <- covdist];
    lst = sort(lst, bool(tuple[str,int] x, tuple[str,int] y) { return x[1] > y[1]; });
    showInteractiveContent(barChart(lst, title="Syntax Coverage for <tests.src.file>"));
}

void testCommands(runSingleTest(Test t)) {
    set[Message] msgs = runTest(t, extractSpec(t));
    // this is ugly; it depends on the success message in runTests
    // so as to avoid making the HTML output red if "success" is the only message.
    if (msgs == {}) {
        msgs += {info("success", t.name.src)};
    }
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


