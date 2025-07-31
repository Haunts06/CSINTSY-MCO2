% Derive parent from father/mother
parent(X, Y) :- father(X, Y).
parent(X, Y) :- mother(X, Y).

% Derive father/mother if parent + gender is known
father(X, Y) :- parent(X, Y), male(X).
mother(X, Y) :- parent(X, Y), female(X).

% Siblings: share at least one parent and are not the same person
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.

% Derive sister and brother from sibling and gender
sister(X, Y) :- sibling(X, Y), female(X).
brother(X, Y) :- sibling(X, Y), male(X).

% Grandparent = parent of parent
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
grandfather(X, Y) :- grandparent(X, Y), male(X).
grandmother(X, Y) :- grandparent(X, Y), female(X).

% Children (used for plural case)
child(X, Y) :- parent(Y, X).
son(X, Y) :- child(X, Y), male(X).
daughter(X, Y) :- child(X, Y), female(X).

% Aunt and Uncle
aunt(X, Y) :- sister(X, Z), parent(Z, Y).
uncle(X, Y) :- brother(X, Z), parent(Z, Y).

% Recursive ancestor relationship
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).


% Avoid infinite recursion on unknown facts
:- dynamic male/1, female/1, parent/2, father/2, mother/2, sibling/2, child/2, brother/2, sister/2, aunt/2, uncle/2, grandparent/2, grandfather/2, grandmother/2, son/2, daughter/2.
