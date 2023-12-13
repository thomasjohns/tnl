# TNL - Table Normalization Language

A domain specific language for transforming tabular data. 

## Contents
* [Example program](#example-program)
* [TNL Concepts](#tnl-concepts)
* [CLI options](#cli-options)
* [Error checking](#error-checking)
* [Features that may be implemented at some point](#features-that-may-be-implemented-at-some-point)
* [Current project status](#current-project-status)
* [Development](#development)
* [Built-in maps](#built-in-maps)
   * [add [number]](#add-number)
   * [mult [number]](#mult-number)
   * [divide [number]](#divide-number)
   * [power [number]](#power-number)
   * [auto_inc](#auto_inc)
   * [round [number]](#round-number)
   * [max [column_selector|number] [column_selector|number]](#max-column_selectornumber-column_selectornumber)
   * [min [column_selector|number] [column_selector|number]](#min-column_selectornumber-column_selectornumber)
   * [mean [column_selector|number] [column_selector|number]](#mean-column_selectornumber-column_selectornumber)
   * [replace_last [string] [string]](#replace_last-string-string)
   * [trim](#trim)
   * [slice [integer] [integer]](#slice-integer-integer)
   * [title](#title)
   * [upper](#upper)
   * [lower](#lower)
   * [remove_prefix [string]](#remove_prefix-string)
   * [remove_suffix [string]](#remove_suffix-string)
   * [concat [string|column_selector] [string|column_selector] [string|column_selector]](#concat-stringcolumn_selector-stringcolumn_selector-stringcolumn_selector)
   * [format [format_string]](#format-format_string)

## Example program
Given the input

| 'date'       | 'name'                 | 'producer'                                                                     |
| ------------ | ---------------------- | ------------------------------------------------------------------------------ |
| '2019-10-5'  | ' parasite '           | 'Kwak Sin-ae; Bong Joon-ho  '                                                  |
| '2018-09-11' | ' green book '         | 'Jim Burke; Charles B. Wessler; Brian Currie; Peter Farrelly; Nick Vallelonga' |
| '2017-08-31' | ' the shape of water ' | 'Guillermo del Toro; J. Miles Dale'                                            |
| '2016-09-02' | ' moonlight '          | 'Adele Romanski; Dede Gardner; Jeremy Kleiner'                                 |

the tnl program:

```
transform Movies {
    headers {
        'date' -> 'Year'
        'name' -> 'Title'
        'producer' -> 'Producer(s)'
    }

    values {
        ['Year'] -> slice 0 4
        ['Title'] -> trim | title | replace 'Of' 'of'
        ['Producer(s)'] -> {
            | trim
            | replace ';' ','
            | replace_last ',' ', and'
        }
    }
}
```

would produce

| 'Year' | 'Title'              | 'Producer(s)'                                                                      |
| ------ | -------------------- | ---------------------------------------------------------------------------------- |
| '2019' | 'Parasite'           | 'Kwak Sin-ae, and Bong Joon-ho'                                                    |
| '2018' | 'Green Book'         | 'Jim Burke, Charles B. Wessler, Brian Currie, Peter Farrelly, and Nick Vallelonga' |
| '2017' | 'The Shape of Water' | 'Guillermo del Toro, and J. Miles Dale'                                            |
| '2016' | 'Moonlight'          | 'Adele Romanski, Dede Gardner, and Jeremy Kleiner'                                 |

This example can be tried from this repo with: `tnl sample/movies.tnl sample/movies.csv`

## TNL Concepts
Right now header and value transforms must exist inside a named `transform`
block, and inside `headers` and `values` blocks. This is temporary. In the
future the program above will be able to be expressed as:
```
'date' -> 'Year'
'name' -> 'Title'
'producer' -> 'Producer(s)'

['Year'] -> slice 0 4
['Title'] -> trim | title | replace 'Of' 'of'
['Producer(s)'] -> {
    | trim
    | replace ';' ','
    | replace_last ',' ', and'
}
```

To map headers, we use the syntax `'from' -> 'to'`, where the left hand side is
a string and the right hand side is an arbitrary map pipeline (in this case it
just returns `'to'`), and the header `from` is mapped to the header `to`.

To map values, we use the syntax `['from'] -> 'to'` where the square brackets
`[]` represent a "column selector". In this case, all the values in the `from`
column are mapped to `to`.

The left-hand-side of the `->` can also be a header pattern or column selector
pattern where a pattern is expressed as `/regex/`. Here are some examples:
```
/.*/ -> trim
[/.*date.*/] -> '2021-01-01'
```
This applies `trim` (deletes leading and trailing spaces) to each header, and
takes any column with header containing `date` and maps all the values to
`2021-01-01`.

The right-hand-side of the `->` is a single or multi-line pipeline. This is a
set of map calls, where data flows left-to-right, top-to-bottom. Right now, TNL
only supports a set of built-in maps (enumerated at the bottom of this page).
Maps in a pipeline are separated by `|`, where a leading `|` is optional. A
single-line pipeline does not have curly braces `{}`, and the pipeline ends at
the end of the line. Multi-line pipelines (a syntactic sugar), must be
expressed in curly braces `{...}`. Different maps take different types of
arguments (`numbers`, `integers`, `strings`, `patterns`, `column_selectors`
etc.). Some can be applied to both `headers` and `values`.

Comments are written with a leading `#`.

## CLI options
There are a few cli options:
- `tnl [src_file] [csv_file] -h`
    - prints
- `tnl [src_file] [csv_file] --print-tokens`
    - prints the tokens recognized by the tnl lexer
- `tnl [src_file] [csv_file] --print-ast`
    - prints the ast nodes constructed by the tnl parser (with indentation)
- `tnl [src_file] [csv_file] --print-code`
    - prints the source code back out as a "pretty print"
- `tnl [src_file] [csv_file] --check`
    - runs semantic analysis and the type checker
- `tnl [src_file] [csv_file] --compile TARGET`  (not implemented yet)
    - outputs some executable program
    - e.g. one planned option is to generate python, pandas code that
      performs the desired tabular data transformation:
        - `tnl src.tnl data.csv --compile pandas`
- `tnl [src_file] [csv_file] --interpret`
    - this is default cli mode
    - this is the same as what gets executed with no provided arguments:
        - `tnl src.tnl data.csv`

## Error checking
- Detect use of a unrecognized built-in map:
    ```
    transform T {
        headers {
            'hello' -> hello 'world'
        }
    }
    ```
    produces:
    ```
    Unrecognized map 'hello'.
    ```
- Detect invalid format string (see `format` in the built-in maps section):
    ```
    transform T {
        headers {
            'hello' -> format ' {planet'
        }
    }
    ```
    produces:
    ```
    Invalid format string (expected '}' before end of string).
    ```
- Detect invalid regex pattern:
    ```
    transform T {
        headers {
            # would likely need to be /.*/
            /*/ -> 'world'
        }
    }
    ```
    produces:
    ```
    Invalid regex pattern /*/.
    ```
- More to be implemented ...

## Features that may be implemented at some point
- [ ] remove need to nest maps in the `transform`, `headers`, and `values` blocks.
- [ ] unary operators
- [ ] binary operators
- [ ] conditionals
- [ ] type checking
- [ ] more symantic analysis checks
- [ ] semantics for creating a new columns
- [ ] semantics for deleting a column
- [ ] semantics for deleting rows
- [ ] semantics for adding rows
- [ ] compilation (e.g. to pandas code)
- [ ] potentially add an IR for optimization and ease of generating code
      (right now execution traverses the AST)
- [ ] variable definitions
- [ ] built-in testing suport
- [ ] library of date built-in functions
- [ ] type casting
- [ ] variadic arguments for certain maps
- [ ] AST and/or IR optimizations

## Current project status
The project is considered pre-alpha. Many components are likely to change.

## Development
- Currently implemented using python 3.9
- Running the tests: `pytest`
- Type checking: `mypy --strict tnl`
- Linting: `flake8 .`

## Built-in maps

### `add [number]`
Add a number to each value in a column.

TNL program:
```
transform Test {
    values {
        ['b'] -> add 2
    }
}
```

csv before:
```
a,b
1,2
3,4
```

csv after:
```
a,b
1,4
3,6
```

### `mult [number]`
Multiply each value in a column by a number.

TNL program:
```
transform Test {
    values {
        ['b'] -> mult 3
    }
}
```

csv before:
```
a,b
1,2
3,4
```

csv after:
```
a,b
1,6
3,12
```

### `divide [number]`
Divide each value in a column by a number.

TNL program:
```
transform Test {
    values {
        ['b'] -> divide 2
    }
}
```

csv before:
```
a,b
1,2
3,4
```

csv after:
```
a,b
1,1
3,2
```

### `power [number]`
Raise each value in a column to a power.

TNL program:
```
transform Test {
    values {
        ['b'] -> power 3
    }
}
```

csv before:
```
a,b
1,2
3,4
```

csv after:
```
a,b
1,8
3,64
```

### `auto_inc`
Assign a column to `1, 2, 3, ..., n-1, n` where `n` is the number of rows in
the input data.

TNL program:
```
transform Test {
    values {
        ['idx'] -> auto_inc
    }
}
```

csv before:
```
idx,a,b
placeholder,1,2
placeholder,3,4
placeholder,5,6
placeholder,7,8
```

csv after:
```
idx,a,b
1,1,2
2,3,4
3,5,6
4,7,8
```

### `round [number]`
Round each value in a column to a some number of decimals.

TNL program:
```
transform Test {
    values {
        ['c'] -> ['b'] | round 1
        ['b'] -> round 0
    }
}
```

csv before:
```
a,b,c
1,1.5,placeholder
3,4.4,placeholder
```

csv after:
```
a,b,c
1,2.0,1.5
3,4.0,4.4
```

### `max [column_selector|number] [column_selector|number]`
Return the max value, comparing each value in a column to each value
in another column, or each value in a column to a number, or just from
comparing two numbers.

TNL program:
```
transform Test {
    values {
        ['c'] -> max ['a'] ['b']
        ['b'] -> max ['b'] 3
        ['a'] -> max 3 5
    }
}
```

csv before:
```
a,b,c
1,2,placeholder
5,4,placeholder
```

csv after:
```
a,b,c
5,3,2
5,4,5
```

### `min [column_selector|number] [column_selector|number]`
Return the min value, comparing each value in a column to each value
in another column, or each value in a column to a number, or just from
comparing two numbers.

TNL program:
```
transform Test {
    values {
        ['c'] -> min ['a'] ['b']
        ['b'] -> min ['b'] 3
        ['a'] -> min 3 5
    }
}
```

csv before:
```
a,b,c
1,2,placeholder
5,4,placeholder
```

csv after:
```
a,b,c
3,2,1
3,3,4
```

### `mean [column_selector|number] [column_selector|number]`
Return the mean value, using each value in a column with each value in
another column, or each value in a column with to a number, or just using
two values.

TNL program:
```
transform Test {
    values {
        ['c'] -> mean ['a'] ['b']
        ['b'] -> mean ['a'] 5
        ['a'] -> mean 1 7
    }
}
```

csv before:
```
a,b,c
1,2,placeholder
3,4,placeholder
```

csv after:
```
a,b,c
4.0,3.0,1.5
4.0,4.0,3.5
```

### `replace_last [string] [string]`
Replace the last instance of a string (in a string) with another string.

TNL program:
```
transform Test {
    headers {
        'a;b;c' -> {
            | replace ';' '; '
            | replace_last '; ' '; and '
        }
    }
    values {
        ['a; b; and c'] -> replace_last 'a' 'b'
    }
}
```

csv before:
```
idx,a;b;c
1,aaaabac
2,aabc
```

csv after:
```
idx,a; b; and c
1,aaaabbc
2,abbc
```

### `trim`
Remove leading and trailing spaces from a header, or form all string values
in a column.

TNL program:
```
transform Test {
    headers {
        /(\\s+.*)|(.*\\s+)/ -> trim
    }
}
```

csv before:
```
 a , b , c,d
1,2,3,4
5,6,7,8
```

csv after:
```
a,b,c,d
1,2,3,4
5,6,7,8
```

### `slice [integer] [integer]`
Return a subset of a string using 0-based indexing.

TNL program:
```
transform Test {
    headers {
        'idx' -> 'Idx'
        'Year-Month-Day' -> slice 0 4
    }
    values {
        ['Year'] -> slice 0 4
    }
}
```

csv before:
```
idx,Year-Month-Day
1,2020-01-01
2,2019-02-15
3,2017-08-02
```

csv after:
```
Idx,Year
1,2020
2,2019
3,2017
```

### `title`
Uppercase the first letter in each word.

TNL program:
```
transform Test {
    headers {
        'idx' -> title
        'message' -> title
    }
    values {
        ['Message'] -> title
    }
}
```

csv before:
```
idx,message
1,hello world
2,hello mars
3,hello andromeda
```

csv after:
```
Idx,Message
1,Hello World
2,Hello Mars
3,Hello Andromeda
```

### `upper`
Uppercase all letters in a string.

TNL program:
```
transform Test {
    headers {
        /b|d/ -> upper
    }
}
```

csv before:
```
a,b,c,d
1,2,3,4
5,6,7,8
```

csv after:
```
a,B,c,D
1,2,3,4
5,6,7,8
```

### `lower`
Lowercase all letters in a string.

TNL program:
```
transform Test {
    headers {
        'B' -> lower
    }
    values {
        ['b'] -> lower
    }
}
```

csv before:
```
A,B
HELLO,WORLD
HELLO,MARS
```

csv after:
```
A,b
HELLO,world
HELLO,mars
```

### `remove_prefix [string]`
Remove the specified string prefix from a string.

TNL program:
```
transform Test {
    headers {
        'noisea' -> remove_prefix 'noise'
    }
    values {
        ['a'] -> remove_prefix 'noise'
    }
}
```

csv before:
```
noisea,b
noisehello,world
noisehello,mars
```

csv after:
```
a,b
hello,world
hello,mars
```

### `remove_suffix [string]`
Remove the specified string suffix from a string.

TNL program:
```
transform Test {
    headers {
        'anoise' -> remove_suffix 'noise'
    }
    values {
        ['a'] -> remove_suffix 'noise'
    }
}
```

csv before:
```
anoise,b
hellonoise,world
hellonoise,mars
```

csv after:
```
a,b
hello,world
hello,mars
```

### `concat [string|column_selector] [string|column_selector] [string|column_selector]`
Join strings together. Right now this map always takes 3 arguments. At some
point it will support a variable number of arguments.

TNL program:
```
transform Test {
    headers {
        'placeholder' -> concat 'hello' ' ' 'message'
    }
    values {
        ['hello message'] -> concat ['a'] ' ' ['b']
    }
}
```

csv before:
```
a,b,placeholder
hello,world,placeholder
hello,mars,placeholder
```

csv after:
```
a,b,hello,message
hello,world,hello world
hello,mars,hello mars
```

### `format [format_string]`
Replace any instance of a `{}` pattern in a string with values passed
into this map. Multiple `{}` can be used in a single format string.
Curly bracket literals can still be used in a string, but they must be
escaped (`\{` or `\}`).

TNL program:
```
transform Test {
    headers {
        'planet' -> format '{} greeting'
    }
    values {
        [/.*planet.*/] -> format 'hello {}'
    }
}
```

csv before:
```
idx,planet
1,earth
2,mars
```

csv after:
```
idx,planet,greeting
1,hello,earth
2,hello,mars
```
