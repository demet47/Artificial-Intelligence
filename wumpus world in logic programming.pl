:- use_module(library(clpfd)).
:- set_prolog_flag(scasp_unknown, fail).
:- style_check(-singleton).
:- discontiguous location/3.
:- discontiguous dir/2.
:- discontiguous action/2.
:- discontiguous bump/1.


location(1,1,1).
dir(1,east).
bump(-5).

action(1,forward).
bump(2).
action(2,clockWise).
action(3,forward).
action(4,counterClockWise).
action(5,forward).
action(6,counterClockWise).


dir(T1,north) :-
T0 #= T1 - 1,
(
((action(T0,hit);action(T0,forward)), dir(T0,north) );
(action(T0,clockWise) , dir(T0,west));
(action(T0,counterClockWise), dir(T0,east))
).


dir(T1,east) :-
T0 #= T1 - 1,
(
((action(T0,hit);action(T0,forward)), dir(T0,east) );
(action(T0,clockWise) , dir(T0,north));
(action(T0,counterClockWise), dir(T0,south))
).


dir(T1,west) :-
T0 #= T1 - 1,
(
((action(T0,hit);action(T0,forward)), dir(T0,west) );
(action(T0,clockWise) , dir(T0,south));
(action(T0,counterClockWise), dir(T0,north))
).


dir(T1,south) :-
T0 #= T1 - 1,
(
((action(T0,hit);action(T0,forward)), dir(T0, south));
(action(T0,clockWise) , dir(T0, east));
(action(T0,counterClockWise), dir(T0,west))
).

location(T1,R,C) :-
T0 is T1 - 1,
RN #= R - 1,
RS #= R + 1,
CW #= C - 1,
CE #= C + 1,
(
((action(T0,clockWise);action(T0,counterClockWise)), location(T0,R,C));
((action(T0,hit);action(T0,forward)), bump(T1), location(T0,R,C));
((action(T0,hit);action(T0,forward)), dir(T0,north), not(bump(T1) ), location(T0,RS,C));
((action(T0,hit);action(T0,forward)), dir(T0,south), not(bump(T1)), location(T0,RN,C));
((action(T0,hit);action(T0,forward)), dir(T0,west), not(bump(T1)), location(T0,R,CE));
((action(T0,hit);action(T0,forward)), dir(T0,east), not(bump(T1)), location(T0,R,CW))
).



wallInFront(T) :-
	FT #= T0 + 1,
    BT #= T0 - 1,
    T0 #> 0,
    bump(FT),
    R #> 0,
    C #> 0,
    RF #= R + 1,
    RB #= R - 1,
    CF #= C + 1,
    CB #= C - 1,
	((dir(T0, south), (action(T0, forward); action(T0, hit)) , location(T0, RF, C));
	(dir(T0, north), (action(T0, forward); action(T0, hit)) , location(T0, RB, C));
	(dir(T0, east), (action(T0, forward); action(T0, hit)) , location(T0, R, CB));
	(dir(T0, west), (action(T0, forward); action(T0, hit)) , location(T0, R, CF))), !.


isWinner(T) :-
    TB is T - 1,
    action(T, hit),
    wumpusInFront(T),!.


wumpusInFront(T) :-
    wumpusSmell(T),
    location(T, R, C),
    T0 #< T,
    0 #< T0,
    C1U #= C-1, C2U #= C-2, C3U #= C-3,
    C1D #= C+1, C2D #= C+2, C3D #= C+3,
    R1L #= R-1, R2L #= R-2, R3L #= R-3,
    R1R #= R+1, R2R #= R+2, R3R #= R+3,
    wumpusSight(T0),
    (
    dir(T, east),
    ( dir(T0, east), (location(T0, R, C3U); location(T0, R, C2U); location(T0, R, C1U)) ),
        \+wumpusNotAround(T,R1R,C), \+wumpusNotAround(T,R1L,C)
    );

    (
    dir(T, west),
    ( dir(T0, west), (location(T0, R, C3D); location(T0, R,C2D); location(T0, R, C1D)) ),
        \+wumpusNotAround(T,R1R,C), \+wumpusNotAround(T,R1L,C)
    );

    (
    dir(T, south),
    ( dir(T0, south), (location(T0, R3R,C ); location(T0, R2R,C); location(T0, R1R,C)) ),
        \+wumpusNotAround(T,R,C1D) , \+wumpusNotAround(T,R,C1U)
    );

    (
    dir(T, north),
    ( dir(T0, north), (location(T0, R3L,C); location(T0, R2L,C); location(T0, R1L,C))),
        \+wumpusNotAround(T,R,C1D) , \+wumpusNotAround(T,R,C1U)
    ).

wumpusNotAround(T, R, C) :-
    T0 #< T,
    0 #< T0,
    C1U #= C-1, C2U #= C-2, C3U #= C-3, C4U #= C-4,
    C1D #= C+1, C2D #= C+2, C3D #= C+3, C4D #= C+4,
    R1L #= R-1, R2L #= R-2, R3L #= R-3, R4L #= R-4,
    R1R #= R+1, R2R #= R+2, R3R #= R+3, R4R #= R+4,
    wumpusSight(T0),
    (dir(T0, east) , (location(T0, R, C3U); location(T0, R, C2U); location(T0, R,C1U); location(T0, R,C4U)) );
    (dir(T0, west), (location(T0, R, C3D); location(T0, R, C2D); location(T0, R, C1D); location(T0, R,C4D)) );
    (dir(T0, south), (location(T0, R3R,C); location(T0, R2R,C); location(T0, R1R,C); location(T0, R4R, C)) );
    (dir(T0, north), (location(T0, R3L,C); location(T0, R2L,C); location(T0, R1L,C); location(T0, R4L,C)) ).

