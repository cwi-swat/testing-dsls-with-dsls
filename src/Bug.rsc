module Bug

import IO;
import Node;

extend lang::std::Layout;
extend lang::std::Id;

syntax Stmt 
  = "if" Expr cond "{" Stmt body "}"
  | Id x "=" Id y
  ;

lexical Expr = [a-z];


void bug() {
    Stmt stmt = (Stmt)`if a { x = y }`;

    stmt2 = visit (stmt) {
        case (Expr)`a` => (Expr)`b`
    }

    // original statement has a source
    println(stmt.src);

    // prints empty map
    println(getKeywordParameters(stmt2));

    // throws exception Undeclared field: src for Tree = appl(Production prod,list[Tree] args)
    println(stmt2.src); 

    // However: the following does work...

    stmt3 = visit (stmt) {
        case (Expr)`a`: insert (Expr)`b`;
        case Stmt _: ;
    }

    // prints map with src entry
    println(getKeywordParameters(stmt3));

    // prints correct loc
    println(stmt3.src); 

}