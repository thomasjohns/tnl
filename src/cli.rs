use polars::prelude::*;
use std::fs::File;
use structopt::StructOpt;

#[derive(Debug, StructOpt)]
struct Opts {
    #[structopt(value_name = "SOURCE_FILE")]
    src_file: String,

    #[structopt(value_name = "TABLE_FILE")]
    table_file: String,
}

pub fn execute() -> std::result::Result<(), String> {
    let opts = Opts::from_args();

    let file = match File::open(&opts.table_file) {
        Ok(res) => res,
        Err(_) => return Err(format!("could not open file {}", opts.table_file)),
    };

    // TODO: move to vm
    let df = CsvReader::new(file)
        .infer_schema(None)
        .has_header(true)
        .finish()
        .unwrap();

    println!("{:?}", df);

    Ok(())
}
