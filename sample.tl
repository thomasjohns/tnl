transform Movies {
    aliases {
        Date = 'Date'
        Title = 'Title'
        Producer = 'Producer(s)'
    }

    headers {
        'date' -> Date
        'name' -> Title
        'producer' -> Producer
    }

    values {
        Date -> slice 0 4
        Title -> trim | title
        Producers -> {
            | trim
            | replace ',' ';'
            | replace_last ',' ', and'
        }
    }
}

# Test rule isn't supported yet
# test Movies {
#     case 'Academy Award Winners' {
#         'date' -> '2019-10-5', '2018-09-11', '2017-08-31', '2016-09-02'
#         'name' -> ' parasite ', ' green book ', ' the shape of water ', ' moonlight '
#         'producer' -> {
#             'Kwak Sin-ae; Bong Joon-ho  ',
#             'Jim Burke; Charles B. Wessler; Brian Currie; Peter Farrelly; Nick Vallelonga',
#             'Guillermo del Toro; J. Miles Dale',
#             'Adele Romanski; Dede Gardner; Jeremy Kleiner'
#         }
#     } becomes {
#         'Date' -> '2019', '2018', '2017', '2016'
#         'Name' -> 'Parasite', 'Green Book', 'The Shape of Water', 'Moonlight'
#         'Producer' -> {
#             'Kwak Sin-ae, and Bong Joon-ho',
#             'Jim Burke, Charles B. Wessler, Brian Currie, Peter Farrelly, and Nick Vallelonga',
#             'Guillermo del Toro, J. Miles Dale',
#             'Adele Romanski, Dede Gardner, and Jeremy Kleiner'
#         }
#     }
# }
