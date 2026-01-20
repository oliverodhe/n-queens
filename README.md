# N-queens Problem

## Experimentation Scope

- **N list:** `[8, 10, 12, 14, 16, 20, 24, 30, 40, 50]`
- **CP time limit:** `60 s/instance`
- **QUBO budget:** `200 reads/N`; `10 trials/N`
- **Success definition:** valid N-queens placement

## Resources

- **Fixstars amplify:** [amplify.fixstars.com](https://amplify.fixstars.com/en/docs/quickstart.html)
- **MiniZinc:** [minizinc.org](https://www.minizinc.org/doc-2.6.4/en/index.html)

## Usage

```bash
python -m src.cli run --ns 4 8 10 --out data/results/results.csv
```
