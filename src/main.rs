mod data;
mod error;
mod model;

use error::Error;
use std::path::Path;

fn main() -> Result<(), Error> {
    let data_dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("data");
    let data = data::read_data(&data_dir)?;

    let lp_plan = model::solve(&data, false)?;
    println!("LP solution");
    println!("-----------");
    for p in &lp_plan.purchases {
        println!("{}: {:.3} packs ({:.0} g)", p.name, p.packs, p.grams);
    }
    println!("Cost: {:.2}€", lp_plan.cost);
    println!();

    let ilp_plan = model::solve(&data, true)?;
    println!("ILP solution");
    println!("------------");
    for p in &ilp_plan.purchases {
        println!("{}: {:.0} packs ({:.0} g)", p.name, p.packs, p.grams);
    }
    println!("Cost: {:.2}€", ilp_plan.cost);

    Ok(())
}
