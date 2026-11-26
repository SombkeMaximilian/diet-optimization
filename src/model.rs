use crate::data::{Data, ENERGY, FoodItem, Limit, Unit};
use crate::error::Error;
use good_lp::{
    Constraint, Expression, ProblemVariables, Solution, SolverModel, Variable, microlp, variable,
};
use std::fmt;
use std::fmt::Formatter;

/// A purchase we make.
#[derive(Clone, PartialEq, Debug)]
pub struct Purchase {
    /// Name of the food item.
    pub name: String,
    /// Number of packs, possibly fractional (LP).
    pub packs: f64,
    /// Total weight of those packs.
    pub grams: f64,
}

/// Purchasing plan.
#[derive(Clone, PartialEq, Debug)]
pub struct Plan {
    /// Total cost of the shopping list.
    pub cost: f64,
    /// Whether the solution only allows integer multiples of each item pack.
    pub integral: bool,
    /// Purchase list.
    pub purchases: Vec<Purchase>,
}

impl fmt::Display for Plan {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        for p in self.purchases.iter() {
            if self.integral {
                writeln!(f, "{}: {:.0} packs ({:.0} g)", p.name, p.packs, p.grams)?;
            } else {
                writeln!(f, "{}: {:.3} packs ({:.0} g)", p.name, p.packs, p.grams)?;
            }
        }
        writeln!(f, "Cost: {:.2}€", self.cost)?;

        Ok(())
    }
}

impl Plan {
    /// Creates a purchasing plan by solving the (integer) linear program.
    pub fn new(data: &Data, days: u32, integral: bool) -> Result<Self, Error> {
        let Data { limits, food_items } = data;
        let days = days as f64;

        let mut vars = ProblemVariables::new();
        let var = if integral {
            variable().integer().min(0)
        } else {
            variable().min(0)
        };
        let packs = vars.add_vector(var, food_items.len());
        let cost = weighted_sum(&packs, food_items, |f| f.price);
        let energy = weighted_sum(&packs, food_items, |f| f.per_pack(ENERGY));

        let mut model = vars.minimise(&cost).using(microlp);
        for limit in limits {
            for constraint in limit_constraints(limit, days, &packs, food_items, &energy)? {
                model.add_constraint(constraint);
            }
        }
        let solution = model.solve()?;
        let purchases = food_items
            .iter()
            .zip(&packs)
            .map(|(food, &x)| (food, solution.value(x)))
            .filter(|&(_, q)| q > 1e-9)
            .map(|(food, q)| Purchase {
                name: food.name.clone(),
                packs: q,
                grams: q * food.weight,
            })
            .collect();

        Ok(Self {
            cost: solution.eval(&cost),
            integral,
            purchases,
        })
    }

    /// Creates a purchasing plan by solving the linear program.
    pub fn fractional(data: &Data, days: u32) -> Result<Self, Error> {
        Self::new(data, days, false)
    }

    /// Creates a purchasing plan by solving the integer linear program.
    pub fn integral(data: &Data, days: u32) -> Result<Self, Error> {
        Self::new(data, days, true)
    }
}

/// Returns `Some(density)` for nutrients with constraints that depend on total
/// energy intake.
fn energy_density(nutrient: &str) -> Option<f64> {
    match nutrient {
        "Sugars" => Some(17.0),
        "Saturated fat" => Some(37.0),
        _ => None,
    }
}

/// Weighted sum of the variables with coefficients depending on the food item.
fn weighted_sum(
    packs: &[Variable],
    foods: &[FoodItem],
    coefficient: impl Fn(&FoodItem) -> f64,
) -> Expression {
    packs
        .iter()
        .zip(foods)
        .map(|(&variable, food)| coefficient(food) * variable)
        .sum()
}

/// Generates the limit constraints.
fn limit_constraints(
    limit: &Limit,
    days: f64,
    packs: &[Variable],
    foods: &[FoodItem],
    energy: &Expression,
) -> Result<Vec<Constraint>, Error> {
    let name = &limit.nutrient;
    let (amount, scale) = match limit.unit {
        Unit::PartTotalEnergy => {
            let kj_per_g =
                energy_density(name).ok_or_else(|| Error::NoEnergyDensity(name.clone()))?;
            (
                weighted_sum(packs, foods, |f| kj_per_g * f.per_pack(name)),
                energy.clone(),
            )
        }
        _ => (
            weighted_sum(packs, foods, |f| f.per_pack(name)),
            Expression::from(1.0),
        ),
    };

    let mut constraints = Vec::new();
    if limit.lower > 0.0 {
        constraints.push(amount.clone().geq(scale.clone() * limit.lower * days));
    }
    if limit.upper.is_finite() {
        constraints.push(amount.leq(scale * limit.upper * days));
    }

    Ok(constraints)
}
