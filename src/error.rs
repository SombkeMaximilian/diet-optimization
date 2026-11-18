use std::fmt;

#[derive(Debug)]
pub enum Error {
    Csv(csv::Error),
    Solver(good_lp::ResolutionError),
    MissingUnit(String),
    MissingNutrient(String),
    NoEnergyDensity(String),
    InvalidNumber { field: &'static str, value: String },
}

impl From<csv::Error> for Error {
    fn from(e: csv::Error) -> Self {
        Self::Csv(e)
    }
}

impl From<good_lp::ResolutionError> for Error {
    fn from(e: good_lp::ResolutionError) -> Self {
        Self::Solver(e)
    }
}

impl std::error::Error for Error {}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Csv(e) => e.fmt(f),
            Error::Solver(e) => e.fmt(f),
            Error::MissingUnit(h) => write!(f, "header '{h}' is missing a unit"),
            Error::MissingNutrient(n) => write!(f, "nutrient '{n}' is missing from food.csv"),
            Error::NoEnergyDensity(n) => write!(f, "no energy density known for '{n}'"),
            Error::InvalidNumber { field, value } => write!(f, "'{value}' is not a valid {field}"),
        }
    }
}
