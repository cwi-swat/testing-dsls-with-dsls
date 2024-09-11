module GenSen

import ParseTree;
import Type;
import util::Math;
import util::Maybe;
import List;
import Set;
import String;
import IO;

loc arbLoc() {
    
    int beginline = arbInt(100);
    int begincolumn = arbInt(40);
    int endline = beginline + abs(arbInt(10));
    int endcolumn = beginline == endline ? begincolumn + abs(arbInt(40)) : arbInt(40);
    int offset = arbInt(500);
    int length = arbInt(300);

    loc dummy = |file:///dummy|(offset,length,<beginline,begincolumn>,<endline,endcolumn>);
    
    return dummy;
}


&T<:Tree genSen(type[&T<:Tree] typ, int depth) 
  = typeCast(typ, genSen(typ.symbol, typ.definitions, depth));

Tree genSen(Symbol s, map[Symbol, Production] defs, int depth) 
  = genSen_(s, defs, depth);

Tree genSen_(label(str l, Symbol s), map[Symbol, Production] defs, int depth) {
  Tree t = genSen(s, defs, depth);
  t.prod.def = label(l, t.prod.def);
  return t;
}

Tree genSen_(\start(s:sort(_)), map[Symbol, Production] defs, int depth)
  = appl(prod(\start(s), [layouts("Standard"), label("top", s), layouts("Standard")], {}), 
        [appl(prod(layouts("Standard"), [], {}), []), 
            genSenProd(defs[s], defs, depth), 
        appl(prod(layouts("Standard"), [], {}), [])
    ], src=arbLoc());

Tree genSen_(s:sort(_), map[Symbol, Production] defs, int depth)
  = genSenProd(defs[s], defs, depth);

Tree genSen_(s:layouts(_), map[Symbol, Production] defs, int depth)
  = appl(p, [char(i) | int i <- chars(" ") ], src=arbLoc())
  when Production p <- defs[s].alternatives;

Tree genSen_(s:lex(_), map[Symbol, Production] defs, int depth)
  = genSenProd(defs[s], defs, depth);

Tree genSenProd(regular(Symbol s), map[Symbol, Production] defs, int depth)
  = genSen(s, defs, depth);

Tree genSenProd(priority(_, list[Production] choices), map[Symbol, Production] defs, int depth)
  = genSen({ p | Production p <- choices }, defs, depth);

Tree genSenProd(associativity(_, _, set[Production] ps), map[Symbol, Production] defs, int depth)
  = genSen(ps, defs, depth);

Tree genSenProd(p:prod(_, list[Symbol] syms, _), map[Symbol, Production] defs, int depth)
  = appl(p, [ genSen(sym, defs, depth - 1) | Symbol sym <- syms ], src=arbLoc());
  
Tree genSenProd(choice(_, set[Production] ps), map[Symbol, Production] defs, int depth)
  = genSen(ps, defs, depth); 

Production chooseProd(set[Production] alts, int depth)
  = depth <= 0 ? smallest(alts) : getOneFrom(alts);

Tree genSen(set[Production] alts, map[Symbol, Production] defs, int depth) 
  = genSenProd(chooseProd(alts, depth), defs, depth);

Tree genSen_(reg:\empty(), map[Symbol, Production] defs, int depth)
  = genSenList(reg, [], defs, depth);

Tree genSen_(reg:\alt(set[Symbol] syms), map[Symbol, Production] defs, int depth) 
  = genSenList(reg, [ getOneFrom(syms) ], defs, depth);

int optLen(int depth) = depth <= 0 ? 0 : arbInt(2);

Tree genSen_(reg:\opt(Symbol s), map[Symbol, Production] defs, int depth) 
  = genSenList(reg, [ s | int _ <- [0..optLen(depth)] ], defs, depth);

Tree genSen_(reg:\seq(list[Symbol] syms), map[Symbol, Production] defs, int depth)
  = genSenList(reg, syms, defs, depth);

Tree genSen_(reg:\iter(Symbol s), map[Symbol, Production] defs, int depth) 
  = genSenIter(reg, defs, depth, 1);

Tree genSen_(reg:\iter-star(Symbol s), map[Symbol, Production] defs, int depth) 
  = genSenIter(reg, defs, depth, 0);

int iterLen(int depth, int minLen) = depth <= 0 ? minLen : minLen + arbInt(10);

Tree genSenIter(Symbol reg, map[Symbol, Production] defs, int depth, int minLen) 
  = genSenList(reg, [ reg.symbol | int _ <- [0..iterLen(depth, minLen)] ], defs, depth);

Tree genSen_(reg:\iter-seps(Symbol sym, list[Symbol] seps), map[Symbol, Production] defs, int depth)
  = genSenIterSep(reg, defs, depth, 1);
  
Tree genSen_(reg:\iter-star-seps(Symbol sym, list[Symbol] seps), map[Symbol, Production] defs, int depth) 
  = genSenIterSep(reg, defs, depth, 0);

int iterSepLen(Symbol reg, int depth, int minLen)
  = depth <= 0 ? minLen : max(minLen,  arbInt(5) * (1 + size(reg.separators)) - size(reg.separators));
  
list[Symbol] iterSepSyms(Symbol reg, int len)
  = [ seq[i % (1 + size(reg.separators))] | int i <- [0..len] ]
  when 
    list[Symbol] seq := [reg.symbol, *reg.separators];
  
Tree genSenIterSep(Symbol reg, map[Symbol, Production] defs, int depth, int minLen) 
  = genSenList(reg, iterSepSyms(reg, iterSepLen(reg, depth, minLen)), defs, depth);

Tree genSenList(Symbol s, list[Symbol] syms, map[Symbol, Production] defs, int depth) 
  = appl(regular(s), [ genSen(sym, defs, depth - 1) | Symbol sym <- syms ], src=arbLoc());

Tree genSen_(\conditional(Symbol s, _), map[Symbol, Production] defs, int depth) 
  = genSen(s, defs, depth); // todo: passs conditions along

Tree genSen_(\lit(str l), map[Symbol, Production] defs, int depth) 
  = appl(prod(\lit(l), [], {}), [ char(i) | int i <- chars(l) ], src=arbLoc());

Tree genSen_(\cilit(str l), map[Symbol, Production] defs, int depth)
  = appl(prod(\cilit(l), [], {}), [ char(i) | int i <- chars(l) ], src=arbLoc());

int chooseChar(list[CharRange] rs)
  = cr.begin + arbInt(max(1, cr.end - cr.begin))
  when 
    CharRange cr := rs[arbInt(size(rs))];

Tree genSen_(\char-class(list[CharRange] rs), map[Symbol, Production] defs, int depth) 
  = char(chooseChar(rs));

int minSize(\empty()) = 0;

int minSize(\opt(_)) = 0;

int minSize(\iter-star(_)) = 0;

int minSize(\iter-star-seps(_, _)) = 0;

int minSize(\iter(_)) = 1;

int minSize(\iter-seps(_, _)) = 1;

int minSize(\alt(set[Symbol] syms)) 
  = ( 1000 | min(it, minSize(s)) | Symbol s <- syms );

int minSize(\seq(list[Symbol] syms))
  = ( 0 | it + minSize(s) | Symbol s <- syms );

default int minSize(Symbol _) = 1;

int minSize(regular(Symbol s)) = minSize(s);

int minSize(prod(_, list[Symbol] syms, _)) 
  = ( 0 | it + minSize(s) | Symbol s <- syms );

int minSize(choice(_, set[Production] alts)) 
  = ( 1000 | min(it, minSize(a)) | Production a <- alts );

int minSize(priority(Symbol def, list[Production] choices))
  = ( 1000 |  min(it, minSize(p)) | Production p <- choices );
  
int minSize(associativity(_, _, set[Production] ps))
  = ( 1000 |  min(it, minSize(p)) | Production p <- ps );

Production smallest(set[Production] prods) 
  = ( getOneFrom(prods) | minSize(p) < minSize(it) ? p : it | Production p <- prods ); 
