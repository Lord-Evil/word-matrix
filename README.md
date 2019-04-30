# word-matrix
Experimental word search project

The idea is that with fixed ruleset, max word length and known alphabet, each word has a predictable position in "matrix", because we get fixed amount of possible words combinations. This way it's easy to calculate exact word's position, knowing it's length and characters.

Possible usage is storing values for those words in matrix, e.g. those could be foregin DB indexes etc.
The bigger matrix is, the bigger it's cell size gets to accommodate every possible numeric value, starting from 0. Probably would be a good case to allow to predefine cell size.

```
Usage:
        ./matrix.py <command> [params] [matrixfile]

Commands:
        c       <alphabet> <wordsize>           Create Matrix
        p       <alphabet> <wordsize>           Just calculate Matrix
        t       <word> <address(int)>           Train Matrix
        tf      <datasetfile>                   Create & Train Matrix from file
        g       <word>                          Read Matrix
        d                                       Dump Matrix data into file
        i                                       Info Matrix
        test                                    Print out sample training dataset
```