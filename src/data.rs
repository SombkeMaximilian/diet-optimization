use crate::error::Error;
use serde::Deserialize;
use std::{collections::BTreeMap, path::Path};

/// Nutrient composition values in food.csv are per 100 g.
const CONVERSION_FACTOR: f64 = 100.0;

/// Energy key.
pub const ENERGY: &str = "Energy";

#[derive(Copy, Clone, Debug, Eq, PartialEq, Deserialize)]
pub enum Unit {
    #[serde(rename = "kJ")]
    KiloJoule,
    #[serde(rename = "g")]
    Gram,
    #[serde(rename = "mg")]
    Milligram,
    #[serde(rename = "µg")]
    Microgram,
    #[serde(rename = "of total energy")]
    PartTotalEnergy,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Limit {
    #[serde(rename = "Nutrient")]
    pub nutrient: String,
    #[serde(rename = "Lower")]
    pub lower: f64,
    #[serde(rename = "Upper")]
    pub upper: f64,
    #[serde(rename = "Unit")]
    pub unit: Unit,
}

#[derive(Clone, Debug)]
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
    /// Amount of `nutrient` in one pack. Presence is checked in `read_data`.
    pub fn per_pack(&self, nutrient: &str) -> f64 {
        self.composition[nutrient] * self.weight / CONVERSION_FACTOR
    }
}

pub struct Data {
    pub limits: Vec<Limit>,
    pub foods: Vec<FoodItem>,
}

pub fn read_data(dir: &Path) -> Result<Data, Error> {
    let limits = read_limits(&dir.join("limits.csv"))?;
    let foods = read_foods(&dir.join("food.csv"))?;
    let required = limits.iter().map(|l| l.nutrient.as_str()).chain([ENERGY]);
    for name in required {
        if foods.iter().any(|f| !f.composition.contains_key(name)) {
            return Err(Error::MissingNutrient(name.to_string()));
        }
    }

    Ok(Data { limits, foods })
}

fn read_limits(path: &Path) -> Result<Vec<Limit>, Error> {
    Ok(csv::Reader::from_path(path)?
        .deserialize()
        .collect::<Result<_, csv::Error>>()?)
}

fn read_foods(path: &Path) -> Result<Vec<FoodItem>, Error> {
    let mut reader = csv::Reader::from_path(path)?;
    let nutrients = reader
        .headers()?
        .iter()
        .skip(3)
        .map(nutrient_name)
        .collect::<Result<Vec<_>, _>>()?;

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

fn nutrient_name(header: &str) -> Result<String, Error> {
    header
        .split_once('[')
        .map(|(name, _)| name.trim().to_string())
        .ok_or_else(|| Error::MissingUnit(header.to_string()))
}

fn parse(value: &str, field: &'static str) -> Result<f64, Error> {
    value.parse().map_err(|_| Error::InvalidNumber {
        field,
        value: value.to_string(),
    })
}
