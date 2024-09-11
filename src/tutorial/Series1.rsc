module tutorial::Series1

import IO;

/*
 * Documentation: https://www.rascal-mpl.org/docs/GettingStarted/
 */

/*
 * Hello world
 *
 * - Import IO, write a function that prints out Hello World!
 * - open the console (click "Import in new Rascal Terminal")
 * - import this module and invoke helloWorld.
 */
 
void helloWorld() {
  println("Hello A-TEST 2024");
} 

/*
 * FizzBuzz (https://en.wikipedia.org/wiki/Fizz_buzz)
 * - To practice some basic programming constructs in Rascal, let us implement two versions of Fizz_buzz
 * - an implementation that solves it imperatively and prints them (fizzBuzz)
 * - another implemention as a list-returning function (fizzBuzzList)
 */
 
void fizzBuzz() {
  //complete

}

list[str] fizzBuzzList() {
  return []; // complete and replace
}

// We can test for fizzBuzzList as follows. Just run from console using :test
// (see https://www.rascal-mpl.org/docs/Rascal/Tests/)
list[str] fbls = ["1","2","Fizz","4","5","Fizz","7","8","Fizz","10","11","Fizz","13","14","Fizz","16","17","Fizz","19","20","Fizz","22","23","Fizz","25","26","Fizz","28","29","Fizz","31","32","Fizz","34","35","Fizz","37","38","Fizz","40","41","Fizz","43","44","Fizz","46","47","Fizz","49","50","Fizz","52","53","Fizz","55","56","Fizz","58","59","Fizz","61","62","Fizz","64","65","Fizz","67","68","Fizz","70","71","Fizz","73","74","Fizz","76","77","Fizz","79","80","Fizz","82","83","Fizz","85","86","Fizz","88","89","Fizz","91","92","Fizz","94","95","Fizz","97","98","Fizz"];
test bool testfizzBuzzList() = fizzBuzzList() == fbls;


/*
 * Factorial
 * - Let us practice some more writing different implementations for the factorial function
 * - first using ordinary structured programming and recursion (fact1)
 * - second using pattern-based dispatch (fact2)
 * - third using switch (fact3) (see https://www.rascal-mpl.org/docs/Rascal/Statements/Switch/)
 */
 
int fact1(int n) {
  return -1; // <- replace
}

int fact2(0) = 1;
int fact2(1) = 1;
//default int fact2(int n) = complete

int fact3(int n) {
  //switch (n) {
  // complete  
  // }
  return -1; // <- replace
}

// Now that we have three implementations, let us write a test let us write a test so they 
// can serve as each other's oracle. For example:
test bool testfactorial0() = fact1(0) == fact2(0);
test bool testfactorial1() = fact1(1) == fact2(1);
test bool testfactorial15() = fact1(15) == fact3(15);
test bool testfactorial1000() = fact2(1000) == fact3(1000);
test bool testfactorial(int n) = n >= 0 && n < 20 ? fact2(n) == fact3(n) : true;


/*
 * Rascal also has comprehensions for generating values.
 * (https://www.rascal-mpl.org/docs/Recipes/BasicProgramming/Comprehensions/)
 * Let us write some examples in the function beloww, you can use println to test the result
 */
 
void comprehensions() {

  // construct a list of squares of integer from 0 to 9 (use range [0..10])
  
  // same, but construct a set
  
  // same, but construct a map

  // construct a list of factorials from 0 to 9
  
  // same, but now only for even numbers  
}
 

/*
 * Pattern matching
 * - fill in the blanks below with pattern match expressions (using :=)
 */
 

void patternMatching() {
  str hello = "Hello World!";
  
  // print all splits of list
  // look at the examples here: https://www.rascal-mpl.org/docs/Rascal/Patterns/List/
  list[int] aList = [1,2,3,4,5];
  for ([/*TODO*/] := aList) {
    ;
  }
  
  // print all partitions of a set
  // loo at th eexamples here: https://www.rascal-mpl.org/docs/Rascal/Patterns/Set/
  set[int] aSet = {1,2,3,4,5};
  for ({/*TODO*/} := aSet) {
    ;
  } 

}  
 
 
 
/*
 * Trees
 * - complete the data type ColoredTree below to represent 
 *   a colored binary tree where each node is either a leaf, a red node, 
 *   or a black node
 * - use the exampleTree() to test your data type in the console
 */
 
 
data ColoredTree
  = leaf(int n);
  

ColoredTree exampleTree()
  =  red(black(leaf(1), red(leaf(2), leaf(3))),
              black(leaf(4), leaf(5)));  
  
  
// write a recursive function summing the leaves
// (use switch or pattern-based dispatch)

int sumLeaves(ColoredTree t) = 0; // TODO: Change this!

// same, but now with visit
int sumLeavesWithVisit(ColoredTree t) {
  return -1; // <- replace
}

// same, but now with a for loop and deep match
int sumLeavesWithFor(ColoredTree t) {
  return -1; // <- replace 
}

// Below you can find another implementation that uses a reducer and deep match.
// The implementation shows a reducer. Reducers in Rascal resemble the fold function found in 
// most functional languages.
// https://www.rascal-mpl.org/docs/Rascal/Expressions/Reducer/
// It has the following syntax: Reducer = ( <initial value> | <some expression with `it` | <generators> )
int sumLeavesWithReducer(ColoredTree t) = ( 0 | it + i | /leaf(int i) := t );


// Complete the function below that adds 1 to all leaves; use visit + =>
ColoredTree inc1(ColoredTree t) {
  return leaf(-1); // <- replace 
}

// Write a test for inc1, run from console using :test
test bool testInc1() = false;

// Define a property for inc1 in the function isInc1, that returns a boolean
// this function should checks if one tree is inc1 of the other
// (without using inc1).
// Use switch on the tupling of t1 and t2 (`<t1, t2>`)
// or pattern based dispatch.
// Hint! The tree also needs to have the same shape!
bool isInc1(ColoredTree t1, ColoredTree t2) {
  return false; // <- replace
}
 
// Write a randomized test for inc1 using the property
// again, execute using :test
test bool testInc1Randomized(ColoredTree t1) = false;