mod data;
mod error;
mod model;

use clap::Parser;
use error::Error;
use std::num::NonZeroU32;
use std::path::Path;

/// Diet optimization program.
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct CliArgs {
    /// Number of days to purchase for.
    #[arg(short, long, default_value_t = NonZeroU32::new(1).unwrap())]
    days: NonZeroU32,
}

fn main() -> Result<(), Error> {
    let args = CliArgs::parse();
    println!(
        "Calculating purchasing plan for {} {}.",
        args.days.get(),
        if args.days.get() == 1 { "day" } else { "days" },
    );
    println!();

    let data_dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("data");
    let data = data::read_data(&data_dir)?;

    let lp_plan = model::Plan::fractional(&data, args.days.get())?;
    println!("LP solution");
    println!("-----------");
    println!("{lp_plan}");
    println!();

    let ilp_plan = model::Plan::integral(&data, args.days.get())?;
    println!("ILP solution");
    println!("------------");
    println!("{ilp_plan}");

    Ok(())
}
