/* FLP project - Turing machine */
/* Author: Jiri Vaclavic, xvacla31 */

/* Dynamic declaration for rules that will be loaded */
:- dynamic rule/4.

/* Reads a line and returns it in L, character by character, until end of file or newline */
read_line(L, C) :-
    get_char(C),
    (isEOFEOL(C), L = [], !; 
    read_line(LL, _), [C|LL] = L).

/* Checks if the character C is EOF or newline */
isEOFEOL(C) :- C == end_of_file; char_code(C, 10).

/* Reads multiple lines until EOF is encountered */
read_lines([]) :- peek_char(end_of_file), !.
read_lines([L|Ls]) :-
    read_line(L, _),
    read_lines(Ls).

/* Removes every second element from a list */
remove_every_second([], []).  
remove_every_second([X], [X]).  
remove_every_second([X, _|T], [X|R]) :-
    remove_every_second(T, R).

/* Splits a line into components */
splitLine([State, Symbol, NewState | Action], State, Symbol, NewState, Action).

/* Creates rules from the list of lines, storing initial string */
createRules([InitString], InitString) :- !.
createRules([Line|Rest], InitString) :-
    remove_every_second(Line, CleanLine),    
    splitLine(CleanLine, State, Symbol, NewState, [Action]),    
    assertz(rule(State, Symbol, NewState, Action)), 
    createRules(Rest, InitString).

/* Checks for presence of a rule transitioning to 'F' */
check_for_F_rule :-
    rule(_, _, 'F', _), 
    !. 
check_for_F_rule :-
    halt(1).

/* Starts the main program */
start :-
    prompt(_, ''),
    read_lines(Input),    
    createRules(Input, InitString),
    check_for_F_rule,
    InitialState = 'S',  
    InitialPosition = 0,  
    applyRules(InitString, InitialState, InitialPosition, [], _),    
    halt.

/* Inserts an element at a specific index in a list */
insert_at(Index, Element, List, Result) :-
    append(Prefix, Suffix, List),
    length(Prefix, Index),
    append(Prefix, [Element], Temp),
    append(Temp, Suffix, Result).

/* Applies rules recursively until a final state 'F' is reached */
applyRules(Tape, 'F', Position, Configs, NewConfigs) :- 
    insert_at(Position, 'F', Tape, TapePrint),
    append(Configs, [TapePrint], NewConfigs),
    maplist(atomic_list_concat, NewConfigs, Strings),
    maplist(writeln, Strings),
    !.

/* Continues to apply rules until a final state is reached */
applyRules(Tape, CurrentState, Position, Configs, _) :-
    insert_at(Position, CurrentState, Tape, TapePrint),
    append(Configs, [TapePrint], RunningConfigs),    
    nth0(Position, Tape, CurrentSymbol, _),
    (   rule_leads_to_target(CurrentState, CurrentSymbol, NewState, Action, 'F')  
    ->  true
    ;   rule(CurrentState, CurrentSymbol, NewState, Action)  
    ),
    applyAction(Action, Tape, Position, NewTape, NewPosition),   
    applyRules(NewTape, NewState, NewPosition, RunningConfigs, _).

/* Special rule handling when transitioning to a target state */
rule_leads_to_target(CurrentState, CurrentSymbol, NewState, Action, TargetState) :-
    rule(CurrentState, CurrentSymbol, NewState, Action),
    NewState = TargetState.

/* Handles rule checking and transitions specifically for the 'F' state */
checkFState(CurrentState, CurrentSymbol, 'F', Action) :-
    rule(CurrentState, CurrentSymbol, 'F', Action), !.  

/* Generic rule checking for any state transition */
checkFState(CurrentState, CurrentSymbol, NewState, Action) :-
    rule(CurrentState, CurrentSymbol, NewState, Action), !.  

/* Additional generic rule handling */
checkFState(CurrentState, _, NewState, Action) :-
    rule(CurrentState, _, NewState, Action),  
    NewState \= 'F',  
    checkFState(CurrentState, _, NewState, Action).  

/* Applies an action 'L' for moving left and handles bounds */
applyAction('L', Tape, Pos, Tape, NewPos) :-
    NewPos is Pos - 1,
    NewPos < 0,
    halt(1).

/* Applies an action 'L' for moving left within bounds */
applyAction('L', Tape, Pos, Tape, NewPos) :-
    NewPos is Pos - 1,
    NewPos >= 0.

/* Applies an action 'R' for moving right */
applyAction('R', Tape, Pos, Tape, NewPos) :-
    NewPos is Pos + 1.

/* Replaces a tape position with a given symbol and maintains tape position */
applyAction(Symbol, Tape, Pos, NewTape, Pos) :-
    (char_type(Symbol, lower); char_type(Symbol, space)),
    replace_position(Tape, Pos, Symbol, NewTape).

/* Utility for replacing a position in a list */
replace_position([_|T], 0, X, [X|T]).
replace_position([H|T], I, X, [H|R]) :-
    I > 0,
    NI is I - 1,
    replace_position(T, NI, X, R).

/* Checks if a character is alphabetic */
is_alpha(X) :-
    char_type(X, alpha).

/* Checks if a character is lowercase */
is_lower_case(Char) :-
    char_type(Char, lower).

/* Prints the tape configuration */
print_configuration(Tape) :-
    atom_chars(TapeString, Tape),
    write(TapeString),nl.
