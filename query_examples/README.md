### Queries Examples 

#### Query 1
    
    query Query1{
        CalculationList{
            ID
        }
    }

#### Query 2

    query Query2{
        CalculatedPropertyList{
            PropertyName
        }
    }


#### Query 3

    query Query3{
        CalculatedPropertyList{
            PropertyName
            numericalValue
        }
    }

#### Query 3
    
    
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
