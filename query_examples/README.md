### Queries Examples 

    
    
    query Query1{
      CalculationList(
        filter:
        {
          _and:[
            {
                ID:{_in:["8473", "10968", "6332", "8088", "21331",
                            "mp-561628", "mp-1127337", "mp-643701"]}
            },
            {
              _or:[
                {
                  hasOutputStructure:{
                    hasComposition:{
                      ReducedFormula:{_in:["MnCl2", "YClO"]}
                    }
                  }
                },
                {
                  hasOutputStructure:{
                    hasComposition:{
                      ReducedFormula:{_in:["CeCrS2O", "SiO2", "O"]}
                    }
                  }
                }
              ]
            }
          ]
        }
      ){
        ID
        hasOutputStructure{
          hasComposition{
            ReducedFormula
          }
        }
      }
    }

    query Query2{
      CalculationList{
        ID
        hasOutputStructure{
          hasComposition{
            ReducedFormula
          }
        }
      }
    }




    query Query1{
      SpaceGroupList{
        SpaceGroupSymbol
      }
    }

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX core: <https://w3id.org/mdo/core/>
PREFIX structure: <https://w3id.org/mdo/structure/>
PREFIX calculation: <https://w3id.org/mdo/calculation/>

SELECT ?sp ?symbol WHERE {
  ?sp rdf:type structure:SpaceGroup;
      structure:SpaceGroupSymbol ?symbol.
} 
```

    query Query2{
      StructureList{
        hasSpaceGroup{
          SpaceGroupSymbol
        }
      }
    }

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX core: <https://w3id.org/mdo/core/>
PREFIX structure: <https://w3id.org/mdo/structure/>
PREFIX calculation: <https://w3id.org/mdo/calculation/>

SELECT ?structure ?sp ?symbol WHERE {
  ?structure rdf:type core:Structure;
             structure:hasSpaceGroup ?sp.
  ?sp rdf:type structure:SpaceGroup;
      structure:SpaceGroupSymbol ?symbol.
}
```

    query Query3{
      StructureList{
        hasSpaceGroup{
          SpaceGroupSymbol
        }
        hasComposition{
          ReducedFormula
        }
      }
    }

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX core: <https://w3id.org/mdo/core/>
PREFIX structure: <https://w3id.org/mdo/structure/>
PREFIX calculation: <https://w3id.org/mdo/calculation/>

SELECT ?structure ?symbol ?reduced_formula WHERE {
  ?structure rdf:type core:Structure;
             structure:hasSpaceGroup ?sp;
             structure:hasComposition ?c.
  ?sp rdf:type structure:SpaceGroup;
      structure:SpaceGroupSymbol ?symbol.
  ?c rdf:type structure:Composition;
     structure:ReducedFormula ?reduced_formula.
}
```

    query Query4{
      CalculationList{
        hasOutputStructure{
          hasSpaceGroup{
            SpaceGroupSymbol
          }
        }
      }
    }

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX core: <https://w3id.org/mdo/core/>
PREFIX structure: <https://w3id.org/mdo/structure/>
PREFIX calculation: <https://w3id.org/mdo/calculation/>

SELECT ?calculation ?structure ?symbol WHERE {
  ?calculation rdf:type core:Calculation;
               core:hasOutputStructure ?structure.
  ?structure rdf:type core:Structure;
             structure:hasSpaceGroup ?sp;
         structure:hasComposition ?c.
  ?sp rdf:type structure:SpaceGroup;
      structure:SpaceGroupSymbol ?symbol.
}
```


    query Query5{
      CalculationList{
        ID
        hasOutputStructure{
          hasSpaceGroup{
            SpaceGroupSymbol
          }
        }
      }
    }

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX core: <https://w3id.org/mdo/core/>
PREFIX structure: <https://w3id.org/mdo/structure/>
PREFIX calculation: <https://w3id.org/mdo/calculation/>

SELECT ?calculation ?structure ?symbol WHERE {
  ?calculation rdf:type core:Calculation;
               core:ID ?id;
               core:hasOutputStructure ?structure.
  ?structure rdf:type core:Structure;
             structure:hasSpaceGroup ?sp;
         structure:hasComposition ?c.
  ?sp rdf:type structure:SpaceGroup;
      structure:SpaceGroupSymbol ?symbol.
}
```

