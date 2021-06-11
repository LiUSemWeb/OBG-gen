### GraphQL and SPARQL Query Examples with filter conditions

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

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    
    SELECT ?subject ?id
    WHERE {
      ?subject rdf:type core:Calculation.
      ?subject core:ID ?id.
      Filter(?id IN ("6332", "8088", "21331","mp-561628", "mp-614918"))
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

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    PREFIX structure: <https://w3id.org/mdo/structure/>
    PREFIX qudt: <http://qudt.org/schema/qudt#>
    
    SELECT ?calculation ?id ?structure1 ?composition1 ?formula1
    WHERE{
        ?calculation rdf:type core:Calculation.
        ?calculation core:ID ?id.
        ?calculation core:hasOutputStructure ?structure1.
        ?structure1 structure:hasComposition ?composition1.
        ?composition1 structure:ReducedFormula ?formula1.
      FILTER EXISTS {
        ?calculation core:hasOutputStructure ?structure2.
        ?structure2 structure:hasComposition ?composition2.
        ?composition2 structure:ReducedFormula ?formula2.
        Filter(?formula2 in ("MnCl2", "YClO"))
      }
      Filter(?id in ("6332", "8088", "21331","mp-561628", "mp-614918"))
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


	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    PREFIX structure: <https://w3id.org/mdo/structure/>
    PREFIX qudt: <http://qudt.org/schema/qudt#>
    
    SELECT ?calculation ?id ?formula1
    WHERE{
        ?calculation rdf:type core:Calculation.
  		?calculation core:ID ?id.
  		?calculation core:hasOutputStructure ?structure1.
  		?structure1 structure:hasComposition ?composition1.
  		?composition1 structure:ReducedFormula ?formula1.
      FILTER EXISTS {
        ?calculation core:hasOutputStructure ?structure2.
    	?calculation core:hasOutputStructure ?structure3.
    	?structure2 structure:hasComposition ?composition2.
  		?composition2 structure:ReducedFormula ?formula2.
    	?structure3 structure:hasComposition ?composition3.
  		?composition3 structure:ReducedFormula ?formula3.
    Filter(?formula2 in ("MnCl2", "YClO") || ?formula3 in ("CeCrS2O", "SiO2", "O"))
      }
    Filter(?id in ("6332", "8088", "21331","mp-561628", "mp-614918"))
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

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    PREFIX structure: <https://w3id.org/mdo/structure/>
    PREFIX qudt: <http://qudt.org/schema/qudt#>
    
    SELECT ?calculation ?id ?formula ?name1 ?value1
    WHERE{
        ?calculation rdf:type core:Calculation.
        ?calculation core:ID ?id.
        ?calculation core:hasOutputStructure ?structure.
        ?calculation core:hasOutputCalculatedProperty ?property1.
        ?structure structure:hasComposition ?composition.
        ?composition structure:ReducedFormula ?formula.
        ?property1 qudt:numericalValue ?value1.
        ?property1 core:PropertyName ?name1.
      FILTER EXISTS {
        ?calculation core:hasOutputCalculatedProperty ?property2.
        ?property2 qudt:numericalValue ?value2.
        ?property2 core:PropertyName ?name2.
        Filter(?value2>5 && ?name2="Band Gap")
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

	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    PREFIX structure: <https://w3id.org/mdo/structure/>
    PREFIX qudt: <http://qudt.org/schema/qudt#>
    
    SELECT ?calculation ?id ?formula ?name1 ?value1
    WHERE{
        ?calculation rdf:type core:Calculation.
        ?calculation core:ID ?id.
        ?calculation core:hasOutputStructure ?structure.
        ?calculation core:hasOutputCalculatedProperty ?property1.
        ?structure structure:hasComposition ?composition.
        ?composition structure:ReducedFormula ?formula.
        ?property1 qudt:numericalValue ?value1.
        ?property1 core:PropertyName ?name1.
      FILTER EXISTS {
        ?calculation core:hasOutputCalculatedProperty ?property2.
        ?property2 qudt:numericalValue ?value2.
        ?property2 core:PropertyName ?name2.
        Filter(?value2>5 && ?name2="Band Gap")
      }
    Filter(?id in ("4698", "12071", "21331","mp-561628", "mp-1592934"))
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

	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    PREFIX structure: <https://w3id.org/mdo/structure/>
    PREFIX qudt: <http://qudt.org/schema/qudt#>
    
    SELECT ?calculation ?id ?formula1 ?name1 ?value1
    WHERE{
        ?calculation rdf:type core:Calculation.
        ?calculation core:ID ?id.
        ?calculation core:hasOutputStructure ?structure1.
        ?calculation core:hasOutputCalculatedProperty ?property1.
        ?structure1 structure:hasComposition ?composition1.
        ?composition1 structure:ReducedFormula ?formula1.
        ?property1 qudt:numericalValue ?value1.
        ?property1 core:PropertyName ?name1.
      FILTER EXISTS {
        ?calculation core:hasOutputCalculatedProperty ?property2.
        ?calculation core:hasOutputStructure ?structure2.
    	?structure2 structure:hasComposition ?composition2.
        ?composition2 structure:ReducedFormula ?formula2.
        ?property2 qudt:numericalValue ?value2.
        ?property2 core:PropertyName ?name2.
    Filter(?value2>5 && ?name2="Band Gap" && ?formula2 in ("MnCl2", "YClO"))
      }
    }