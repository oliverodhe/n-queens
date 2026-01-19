int: n;
array[1..n, 1..n] of var 0..1: x; % x[r,c] = 1 if queen at (r,c)

% Exactly one queen per row
constraint forall(r in 1..n) (
  sum(c in 1..n)(x[r,c]) = 1
);

% Exactly one queen per column
constraint forall(c in 1..n) (
  sum(r in 1..n)(x[r,c]) = 1
);

% Diagonals: r - c constant (top-left to bottom-right)
constraint forall(d in -(n-1)..(n-1)) (
  sum(r in 1..n, c in 1..n where r - c = d)(x[r,c]) <= 1
);

% Anti-diagonals: r + c constant (top-right to bottom-left)
constraint forall(s in 2..(2*n)) (
  sum(r in 1..n, c in 1..n where r + c = s)(x[r,c]) <= 1
);

solve satisfy;

output [
  "n=", show(n), "\n",
  "board=\n"
] ++
[
  if fix(x[r,c]) = 1 then "Q " else ". " endif ++
  if c = n then "\n" else "" endif
  | r in 1..n, c in 1..n
];