### GraphQL and SPARQL Query Examples without filter conditions

#### Query 1: List calculation objects with IDs
    query Query1{
        CalculationList{
            ID
        }
    }


    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    SELECT ?calculation ?id WHERE {
      ?calculation rdf:type core:Calculation;
                   core:ID ?id.
    } 

#### Query 2: List calculated properties with PropertyNames
    query Query2{
        CalculatedPropertyList{
            PropertyName
        }
    }


    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    SELECT ?calculatedproperty ?name WHERE {
      ?calculatedproperty rdf:type core:CalculatedProperty;
                          core:PropertyName ?name.
    } 
#### Query 3: List calculated properties with PropertyNames and numericalValue
    query Query3{
        CalculatedPropertyList{
            PropertyName
            numericalValue
        }
    }

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    PREFIX qudt: <http://qudt.org/schema/qudt#>
    SELECT ?calculatedproperty ?name ?value WHERE {
      ?calculatedproperty rdf:type core:CalculatedProperty;
               core:PropertyName ?name;
               qudt:numericalValue ?value.
    } 
#### Query 4: List compositions with ReducedFormulas
    query Query4{
        CompositionList{
            ReducedFormula
        }
    }

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX structure: <https://w3id.org/mdo/structure/>
    SELECT ?composition ?formula WHERE {
      ?composition rdf:type structure:Composition;
                   structure:ReducedFormula ?formula.
    } 

#### Query 5: List structures including compositions' ReducedFormulas
    query Query5{
        StructureList{
            hasComposition{
                ReducedFormula
            }
        }
    }

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX core: <https://w3id.org/mdo/core/>
    PREFIX structure: <https://w3id.org/mdo/structure/>
    SELECT ?structure ?composition ?formula WHERE {
      ?structure rdf:type core:Structure;
                 structure:hasComposition ?composition.
      ?composition rdf:type structure:Composition;
                   structure:ReducedFormula ?formula.
    } 
#### Query 6: List calculations including ReducedFormulas
    query Query6{
        CalculationList{
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
    SELECT ?calculation ?structure ?composition ?formula WHERE {
      ?calculation rdf:type core:Calculation;
                   core:hasOutputStructure ?structure.
      ?structure rdf:type core:Structure;
                 structure:hasComposition ?composition.
      ?composition rdf:type structure:Composition;
                   structure:ReducedFormula ?formula.
    } 
#### Query 7: List calculations including the ID and ReducedFormulas
    query Query7{
        CalculationList{
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
    SELECT ?calculation ?id ?structure ?composition ?formula WHERE {
      ?calculation rdf:type core:Calculation;
                   core:ID ?id;
                   core:hasOutputStructure ?structure.
      ?structure rdf:type core:Structure;
                 structure:hasComposition ?composition.
      ?composition rdf:type structure:Composition;
                   structure:ReducedFormula ?formula.
    } 
#### Query 8: List calculations including calculatedproperty PropertyNames and numericalValues
    query Query8{
        CalculationList{
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
    SELECT ?calculation ?calculatedproperty ?name ?value WHERE {
      ?calculation rdf:type core:Calculation;
                   core:hasOutputCalculatedProperty ?calculatedproperty.
      ?calculatedproperty rdf:type core:CalculatedProperty;
                   core:PropertyName ?name;
                   qudt:numericalValue ?value.
    } 
#### Query 9: List calculations including ID, calculatedproperty PropertyNames and numericalValues
    query Query9{
        CalculationList{
            ID
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
    
    SELECT ?calculation ?id ?calculatedproperty ?name ?value WHERE {
        ?calculation rdf:type core:Calculation;
                              core:hasOutputCalculatedProperty ?calculatedproperty;
                              core:ID ?id.
        ?calculatedproperty rdf:type core:CalculatedProperty;
                            core:PropertyName ?name;
                            qudt:numericalValue ?value.
    }
#### Query 10: List calculations including ID, ReducedFormulas, calculatedproperty PropertyNames and numericalValues
    query Query10{
        CalculationList{
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
    SELECT ?calculation ?id ?calculatedproperty ?name ?value WHERE {
      ?calculation rdf:type core:Calculation;
                   core:ID ?id;
                   core:hasOutputCalculatedProperty ?calculatedproperty;
                   core:hasOutputStructure ?structure.
  	  ?structure rdf:type core:Structure;
                 structure:hasComposition ?composition.
      ?composition rdf:type structure:Composition;
                   structure:ReducedFormula ?formula.
      ?calculatedproperty rdf:type core:CalculatedProperty;
                   core:PropertyName ?name;
                   qudt:numericalValue ?value.
    } 