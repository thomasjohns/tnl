# TNL - Table Normalization Lanugage

A domain specific language for transforming tabular data. For example, given the input

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
        ['Title'] -> trim | title
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

Sample usage: `tnl src_file.tnl input_file.csv`

The project is work in progress.
