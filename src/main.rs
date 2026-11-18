mod data;
mod error;
mod model;

use error::Error;
use std::path::Path;

fn main() -> Result<(), Error> {
    let data_dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("data");
    let data = data::read_data(&data_dir)?;

    let lp_plan = model::Plan::new(&data, false)?;
    println!("LP solution");
    println!("-----------");
    println!("{lp_plan}");
    println!();

    let ilp_plan = model::Plan::new(&data, true)?;
    println!("ILP solution");
    println!("------------");
    println!("{ilp_plan}");

    Ok(())
}
