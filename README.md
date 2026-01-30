# N-queens Problem

## Experimentation Scope

- **N list:** `[8, 10, 12, 14, 16, 20, 24, 30, 40, 50]`
- **CP time limit:** `60 s/instance`
- **QUBO budget:** `200 reads/N`; `10 trials/N`
- **Success definition:** valid N-queens placement

## Resources

- **Fixstars amplify:** [amplify.fixstars.com](https://amplify.fixstars.com/en/docs/quickstart.html)
- **MiniZinc:** [minizinc.org](https://www.minizinc.org/doc-2.6.4/en/index.html)

## Environment

Add the amplify API token to a `.env` file and export:

```bash
set -a
source .env
set +a 
```

## CLI

Genarate results:

```bash
python -m src.cli run --ns 8 10 12 14 16 --out data/results/results.csv
```

Summarize:

```bash
python -m src.cli summarize --in data/results/results.csv --out data/results/summary.csv
```

Plot:

```bash
python -m src.cli plot --summary data/results/summary.csv --outdir data/results
```
