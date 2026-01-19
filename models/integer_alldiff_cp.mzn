int: n;
array[1..n] of var 1..n: q; % q[r] = column of queen in row r

include "alldifferent.mzn";

constraint alldifferent(q);
constraint alldifferent([ q[r] + r | r in 1..n ]);
constraint alldifferent([ q[r] - r | r in 1..n ]);

solve satisfy;

output [
  "n=", show(n), "\n",
  "q=", show(q), "\n"
];