### GraphQL and SPARQL Query Examples without filter conditions

#### Query 1: List calculations where the ID in a given range
    query Query1{
      CalculationList(
        filter:{
          ID:{
            _in:["6332", "8088", "21331","mp-561628", "mp-614918"]
          }
        }){
        ID
      }
    }



#### Query 2: CQ6 (simple filter condition (A&B)): For a series of materials calculations, what are the compositions of materials with a specific range of a calculated property (e.g., band gap)?
    query Query2{
      CalculationList(
        filter:{
          _and:[
            {ID:{_in:["6332", "8088", "21331","mp-561628", "mp-614918"]}},
            {
              hasOutputStructure:{
                hasComposition:{
                  ReducedFormula:{_in:["MnCl2", "YClO"]}
                }
              }      
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


####Query 3: CQ6 (complex filter condition (A & (B|C))): For a series of materials calculations, what are the compositions of materials with a specific range of a calculated property (e.g., band gap)?

    query Query3{
      CalculationList(
        filter:{
          _and:
          [
            {ID:{_in:["6332", "8088", "21331","mp-561628", "mp-614918"]}},
            {
              _or:
              [
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

####Query 4: List calculations of which the value of band gap is greater than 5.

    query Query4{
      CalculationList(
        filter:{
          hasOutputCalculatedProperty:{
            _and:[
              {
                PropertyName:{_eq: "Band Gap"}
              },
              {
                numericalValue:{_gt:5}
                }
            ]
          }
        }
      ){
        ID
        hasOutputStructure{
          hasComposition{
            ReducedFormula
          }
        }
        hasOutputCalculatedProperty{
          PropertyName
          numericalValue
        }
      }
    }

####Query 5: List calculations of which the value of band gap is greater than 5 and calculation ID is in a given range.

    query Query5{
      CalculationList(
        filter:{
          _and:[
            {
              ID:{_in:["4698", "12071", "21331","mp-561628", "mp-1592934"]}
            },
            {
              hasOutputCalculatedProperty:{
                _and:
                [
                  {
                    PropertyName:{_eq: "Band Gap"}
                  },
                  {
                    numericalValue:{_gt:5}
                  }
                    ]
                }
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
        hasOutputCalculatedProperty{
          PropertyName
          numericalValue
        }
      }
    }

####Query 6: List calculations of which the value of band gap is greater than 5 and ReducedFormula is in a given range.

    query Query6{
      CalculationList(
        filter:{
          _and:[
            {
                  hasOutputStructure:{
                    hasComposition:{
                      ReducedFormula:{_in:["MnCl2", "YClO"]}
                    }
                  }
            },
            {
              hasOutputCalculatedProperty:{
                _and:
                [
                  {
                    PropertyName:{_eq: "Band Gap"}
                  },
                  {
                    numericalValue:{_gt:5}
                  }
                ]
              }
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
        hasOutputCalculatedProperty{
          PropertyName
          numericalValue
        }
      }
    }