:- dynamic relative/2, male/1, female/1, parent/2, father/2, 
           mother/2, sibling_fact/2, child/2, brother/2, 
           sister/2, aunt/2, uncle/2, grandparent/2, 
           grandfather/2, grandmother/2, son/2, daughter/2.


% Entry point
relative(X, Y) :- relative(X, Y, []).

% Stop if already visited
relative(X, Y, Visited) :-
    \+ member((X, Y), Visited),
    (
        parent(X, Y);
        parent(Y, X);
        sibling(X, Y);
        grandparent(X, Y);
        grandparent(Y, X);
        aunt(X, Y);
        aunt(Y, X);
        uncle(X, Y);
        uncle(Y, X)
    ).

% Recursive case with visited check
relative(X, Y, Visited) :-
    \+ member((X, Y), Visited),
    (
        parent(X, Z);
        parent(Z, X);
        sibling(X, Z);
        grandparent(X, Z);
        grandparent(Z, X);
        aunt(X, Z);
        uncle(X, Z)
    ),
    relative(Z, Y, [(X, Y) | Visited]).

parent(X, Y) :- father(X, Y).
parent(X, Y) :- mother(X, Y).
parent(X, Y) :- father(X, Y), male(X).
parent(X, Y) :- mother(X, Y), female(X).


% Children and gendered children (only derive from parent facts)
child(X, Y)    :- parent(Y, X).
son(X, Y)      :- child(X, Y), male(X).
daughter(X, Y) :- child(X, Y), female(X).

% Gendered sibling rules (1-way)
brother(X, Y) :- male(X), sibling(X, Y).
sister(X, Y)  :- female(X), sibling(X, Y).

% Core sibling logic: shared parent or explicitly declared
sibling(X, Y) :-
    (sibling_fact(X, Y); sibling_fact(Y, X));
    (parent(Z, X), parent(Z, Y), X \= Y).

% Transitive sibling relation
related_sibling(X, Y) :- related_sibling(X, Y, []).
related_sibling(X, Y, _) :- sibling(X, Y), X \= Y.
related_sibling(X, Y, Visited) :- 
    sibling(X, Z),
    Z \= X,
    \+ member(Z, Visited),
    related_sibling(Z, Y, [X|Visited]),
    X \= Y.


% Grandparents
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
grandfather(X, Y) :- grandparent(X, Y), male(X).
grandmother(X, Y) :- grandparent(X, Y), female(X).

% Aunt/Uncle
aunt(X, Y)     :- sister(X, Z), parent(Z, Y).
uncle(X, Y)    :- brother(X, Z), parent(Z, Y).

% Recursive ancestor
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
