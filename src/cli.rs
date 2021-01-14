use std::fs::File;
use structopt::StructOpt;

#[derive(Debug, StructOpt)]
struct Opts {
    #[structopt(value_name = "SOURCE_FILE")]
    src_file: String,

    #[structopt(value_name = "TABLE_FILE")]
    table_file: String,

    #[structopt(long, value_name = "STAGE", default_value = "exec")]
    stage: String,
}

pub enum Stage {
    Lex,
    Parse,
    Analyze,
    Compile,
    Optimize,
    Exec,
}

pub struct Config {
    pub stage: Stage,
    pub src_file: File,
    pub table_file: File,
}

pub fn execute() -> Result<Config, String> {
    let opts = Opts::from_args();

    let src_file = match File::open(&opts.src_file) {
        Ok(res) => res,
        Err(_) => return Err(format!("could not open source file '{}'", opts.src_file)),
    };

    let table_file = match File::open(&opts.table_file) {
        Ok(res) => res,
        Err(_) => return Err(format!("could not open table file '{}'", opts.table_file)),
    };

    let stage = match &opts.stage[..] {
        "lex" => Stage::Lex,
        "parse" => Stage::Parse,
        "analyze" => Stage::Analyze,
        "compile" => Stage::Compile,
        "optimze" => Stage::Optimize,
        "exec" => Stage::Exec,
        s => return Err(format!("unknown stage '{}'", s)),
    };

    Ok(Config {
        stage: stage,
        src_file: src_file,
        table_file: table_file,
    })
}
