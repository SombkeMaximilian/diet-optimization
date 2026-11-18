# Diet Optimization

Known as [Stigler diet](https://en.wikipedia.org/wiki/Stigler_diet). This repository contains a more modern,
medium-effort dataset for Stigler's diet optimization problem in a German context.

## Notable additions

- metric system
- more nutrients
- upper limits for nutrients (e.g., sodium)
- inclusion of vegan products
- new kind of constraint (part of total energy)

## Dataset

Uses the version 4.0 data from the German [BLS (Max Rubner-Institut (2025))](https://doi.org/10.25826/Data20251217-134202-0).
See `data/README.md` for how to obtain the dataset this repository provides.

## Solution

Follow the instructions above to generate the dataset. Install Rust and Cargo from [rustup](https://rustup.rs/)
and run the following command:

```bash
RUSTFLAGS="-C target-cpu=native" cargo run --release
```

## License

Public domain.
