use crate::data::{Data, ENERGY, FoodItem, Limit, Unit};
use crate::error::Error;
use good_lp::{
    Constraint, Expression, ProblemVariables, Solution, SolverModel, Variable, microlp, variable,
};

pub struct Purchase {
    pub name: String,
    pub packs: f64,
    pub grams: f64,
}

pub struct Plan {
    pub cost: f64,
    pub purchases: Vec<Purchase>,
}

fn energy_density(nutrient: &str) -> Option<f64> {
    match nutrient {
        "Sugars" => Some(17.0),
        "Saturated fat" => Some(37.0),
        _ => None,
    }
}

fn weighted_sum(
    packs: &[Variable],
    foods: &[FoodItem],
    coef: impl Fn(&FoodItem) -> f64,
) -> Expression {
    packs
        .iter()
        .zip(foods)
        .map(|(&x, food)| coef(food) * x)
        .sum()
}

fn limit_constraints(
    limit: &Limit,
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
        constraints.push(amount.clone().geq(scale.clone() * limit.lower));
    }
    if limit.upper.is_finite() {
        constraints.push(amount.leq(scale * limit.upper));
    }
    Ok(constraints)
}

pub fn solve(data: &Data, integral: bool) -> Result<Plan, Error> {
    let Data { limits, foods } = data;

    let mut vars = ProblemVariables::new();
    let var = if integral { variable().integer().min(0) } else { variable().min(0) };
    let packs = vars.add_vector(var, foods.len());

    let cost = weighted_sum(&packs, foods, |f| f.price);
    let energy = weighted_sum(&packs, foods, |f| f.per_pack(ENERGY));

    let mut model = vars.minimise(&cost).using(microlp);
    for limit in limits {
        for constraint in limit_constraints(limit, &packs, foods, &energy)? {
            model.add_constraint(constraint);
        }
    }
    let solution = model.solve()?;

    let purchases = foods
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

    Ok(Plan {
        cost: solution.eval(&cost),
        purchases,
    })
}
