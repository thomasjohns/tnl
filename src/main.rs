mod ast;
mod cli;
mod ir;
mod irgen;
mod lexer;
mod optimizer;
mod parser;
mod symbol;
mod symbolgen;
mod vm;

use polars::prelude::*;

fn main() {
    let config = match cli::execute() {
        Ok(c) => c,
        Err(err) => {
            eprintln!("error: {}", err);
            std::process::exit(1);
        }
    };

    // TODO: move to vm
    let df = CsvReader::new(config.table_file)
        .infer_schema(None)
        .has_header(true)
        .finish()
        .unwrap();

    println!("{:?}", df);
}
