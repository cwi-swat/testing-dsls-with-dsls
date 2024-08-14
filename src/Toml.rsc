module Toml

lexical WSChar = [\ \t\n];

lexical Comment = "#" ![\n]* $;

lexical WhiteSpaceOrComment = WSChar | Comment;

layout Whitespace = WhiteSpaceOrComment* !>> [\ \t\n #];

// Overall Structure
start syntax TOML = Section*;

syntax Section = Table Keyval*;

// syntax Expression
//     = Keyval 
//     | Table 
//     ;


lexical NonAscii = [\u0080-\uD7FF] | [\uE000-\u10FFFF];


// Key-Value Pairs
syntax Keyval = Key "=" Val ;
syntax Key = SimpleKey | DottedKey ;
syntax SimpleKey = QuotedKey | UnquotedKey;
syntax UnquotedKey = [A-Za-z0-9_\-]+;
syntax QuotedKey = BasicString | LiteralString;
syntax DottedKey = {SimpleKey "."}+ ;

syntax Val = String | Boolean | Array | InlineTable | DateTime | Float | Integer ;

// String
syntax String = MLBasicString | BasicString | MLLiteralString | LiteralString ;

// Basic String
syntax BasicString = "\"" BasicChar* "\"" ;
lexical BasicChar = BasicUnescaped | Escaped;
lexical BasicUnescaped =  [\u0021] | [\u0023-\u005B] | [\u005D-\u007E] | NonAscii;
lexical Escaped = Escape EscapeSeqChar;
lexical Escape = "\\" ;
lexical EscapeSeqChar = "\"" | "\\" | "b" | "f" | "n" | "r" | "t" 
                       | "u" HEXDIG HEXDIG HEXDIG HEXDIG
                       | "U" HEXDIG HEXDIG HEXDIG HEXDIG HEXDIG HEXDIG HEXDIG HEXDIG ;

lexical HEXDIG = [0-9a-fA-F];


// Multiline Basic String
syntax MLBasicString = "\"\"\"" NewLine? MLBasicBody "\"\"\"";
syntax MLBasicBody = MLBContent* (MLBQuotes MLBContent+) MLBQuotes? ;

syntax MLBContent = MLBChar | NewLine | MLBEscapedNL;
lexical MLBChar = MLBUnescaped | Escaped;
lexical MLBQuotes =  "\"" | ("\"" "\"");
lexical MLBUnescaped =  [\u0021\u0023-\u005B\u005D-\u007E] | NonAscii;
lexical MLBEscapedNL = Escape NewLine+ (WSChar | NewLine)* ;

// Literal String
lexical LiteralString = "\'" ([\u0009\u0020-\u0026\u0028-\u007E] | NonAscii)* "\'" ;

// Multiline Literal String
syntax MLLiteralString = "\'\'\'" NewLine? MLLiteralBody "\'\'\'";
syntax MLLiteralBody = MLLContent* (MLLQuotes MLLContent+)* MLLQuotes? ;

syntax MLLContent = MLLChar | NewLine;
lexical MLLChar = [\u0009\u0020-\u0026\u0028-\u007E] | NonAscii;
lexical MLLQuotes = "\'" | ("\'" "\'");


// Integer

syntax Integer = DecInt | HexInt | OctInt | BinInt ;

lexical DecInt = [+\-]? UnsignedDecInt;
lexical UnsignedDecInt = [0-9] | [1-9] ("_"? [0-9])+;

lexical HexInt = "0x" [0-9ABCDEF] ("_"? [0-9ABCDEF])*;
lexical OctInt = "0o" [0-7] ("_"? [0-7])*;
lexical BinInt = "0b" [0-1] ("_"? [0-1])*;

// Float
syntax Float
    = FloatIntPart (Exp | (Frac Exp?))
    | SpecialFloat;

syntax FloatIntPart = DecInt;
syntax Frac = "." ZeroPrefixableInt;
syntax ZeroPrefixableInt = [0-9] ("_"? [0-9])*;
syntax Exp = "e" FloatExpPart;
syntax FloatExpPart = [+\-]? ZeroPrefixableInt;

lexical SpecialFloat = [+\-]? ("inf" | "nan");

// Boolean
syntax Boolean = "true" | "false";

// Date and Time
syntax DateTime = OffsetDateTime | LocalDateTime | LocalDate | LocalTime ;

lexical TimeOffset = "Z" | ([+\-] [0-9] [0-9] ":" [0-9] [0-9]);

syntax PartialTime = [0-9] [0-9] ":" [0-9] [0-9] ":" [0-9] [0-9] ("."[0-9]+)?;
syntax FullDate = [0-9] [0-9] [0-9] [0-9] "-" [0-9] [0-9] "-" [0-9] [0-9];
syntax FulleTime = PartialTime TimeOffset;

syntax OffsetDateTime = FullDate [Tt ] FulleTime;
syntax LocalDateTime = FullDate [Tt ] PartialTime;
syntax LocalDate = FullDate;
syntax LocalTime = PartialTime;

// Array
syntax Array = "[" {Val ","}* ","?  "]";


// Table
syntax Table = StdTable | ArrayTable ;

syntax StdTable = "[" Key "]" ;

// Inline Table

syntax InlineTable = "{"  {Keyval ","}*  "}" ;

// Array Table
syntax ArrayTable = "[[" Key "]]";