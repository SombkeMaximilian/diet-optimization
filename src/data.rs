use crate::error::Error;
use serde::Deserialize;
use std::{collections::BTreeMap, path::Path};

/// Nutrient composition values in food.csv are per 100 g.
const CONVERSION_FACTOR: f64 = 100.0;

/// Energy key.
pub const ENERGY: &str = "Energy";

/// Units that appear in the data.
#[derive(Copy, Clone, Debug, Eq, PartialEq, Deserialize)]
pub enum Unit {
    /// Energy is always given in units of kilo Joule.
    #[serde(rename = "kJ")]
    KiloJoule,
    /// All food item pack sizes and some nutrients are given in units of grams.
    #[serde(rename = "g")]
    Gram,
    /// Some minerals and vitamins are given in units of milligrams.
    #[serde(rename = "mg")]
    Milligram,
    /// Some minerals and vitamins are given in units of micrograms.
    #[serde(rename = "µg")]
    Microgram,
    /// Constraints imposed on how much of the total energy a nutrient may be.
    #[serde(rename = "of total energy")]
    PartTotalEnergy,
}

/// Daily minimum required and maximum tolerable amounts of a nutrient.
#[derive(Clone, PartialEq, Debug, Deserialize)]
pub struct Limit {
    /// Common name of the nutrient.
    #[serde(rename = "Nutrient")]
    pub nutrient: String,
    /// Lowest required amount `(>= 0)`.
    #[serde(rename = "Lower")]
    pub lower: f64,
    /// Maximum tolerable amount `(<= +inf)`.
    #[serde(rename = "Upper")]
    pub upper: f64,
    /// Unit of the bounds.
    #[serde(rename = "Unit")]
    pub unit: Unit,
}

/// Purchasable food item.
#[derive(Clone, PartialEq, Debug)]
pub struct FoodItem {
    /// Common name of the item.
    pub name: String,
    /// Price in Euros.
    pub price: f64,
    /// Weight of one pack in grams.
    pub weight: f64,
    /// Nutrient amounts per 100 g.
    composition: BTreeMap<String, f64>,
}

impl FoodItem {
    /// Amount of `nutrient` in one pack.
    ///
    /// The presence of all possible nutrients is checked in [`read_data`].
    ///
    /// # Panics
    ///
    /// Panics if a nutrient that isn't included is passed.
    pub fn per_pack(&self, nutrient: &str) -> f64 {
        self.composition[nutrient] * self.weight / CONVERSION_FACTOR
    }
}

/// Bundled data.
#[derive(Clone, PartialEq, Debug)]
pub struct Data {
    /// Daily limits of nutrients.
    pub limits: Vec<Limit>,
    /// Available food items.
    pub food_items: Vec<FoodItem>,
}

/// Reads the nutrient limits and food items table from the data directory.
///
/// # Errors
///
/// Returns an error if reading either of them fails, or if the nutrient
/// lists are not consistent between them.
pub fn read_data(dir: &Path) -> Result<Data, Error> {
    let limits = read_limits(&dir.join("limits.csv"))?;
    let foods = read_food(&dir.join("food.csv"))?;
    let required = limits.iter().map(|l| l.nutrient.as_str()).chain([ENERGY]);
    for name in required {
        if foods.iter().any(|f| !f.composition.contains_key(name)) {
            return Err(Error::MissingNutrient(name.to_string()));
        }
    }

    Ok(Data {
        limits,
        food_items: foods,
    })
}

/// Reads the nutrient limits from the path pointing to `limits.csv`.
fn read_limits(path: &Path) -> Result<Vec<Limit>, Error> {
    Ok(csv::Reader::from_path(path)?
        .deserialize()
        .collect::<Result<Vec<Limit>, csv::Error>>()?)
}

/// Reads the food items from the path pointing to `food.csv`.
fn read_food(path: &Path) -> Result<Vec<FoodItem>, Error> {
    let mut reader = csv::Reader::from_path(path)?;
    let nutrients = reader
        .headers()?
        .iter()
        .skip(3)
        .map(|header| {
            header
                .split_once('[')
                .map(|(name, _)| name.trim().to_string())
                .ok_or_else(|| Error::MissingUnit(header.to_string()))
        })
        .collect::<Result<Vec<String>, Error>>()?;

    reader
        .records()
        .map(|record| {
            let record = record?;
            let composition = nutrients
                .iter()
                .zip(record.iter().skip(3))
                .map(|(name, value)| Ok((name.clone(), parse(value, "nutrient amount")?)))
                .collect::<Result<_, Error>>()?;
            Ok(FoodItem {
                name: record[0].to_string(),
                price: parse(&record[1], "price")?,
                weight: parse(&record[2], "weight")?,
                composition,
            })
        })
        .collect()
}

/// Parses value as an `f64` and returns the appropriate [`Error`] upon failure.
fn parse(value: &str, field: &'static str) -> Result<f64, Error> {
    value.parse().map_err(|_| Error::InvalidNumber {
        field,
        value: value.to_string(),
    })
}
