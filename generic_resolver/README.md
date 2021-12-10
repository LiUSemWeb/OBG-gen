## Getting Started

*  [obg_gen_graphql_utils.py](./obg_gen_graphql_utils.py) implements the generic resolver function.  
*  [mapping_utils.py](./mapping_utils.py) defines functions to parse RML mappings.
*  [filter_utils.py](./filter_utils.py) defines functions used to parse filtering conditions.
*  [filter_ast.py](./filter_ast.py) defines functions to generate the abstract syntax trees for representing the filtering condition entailed with a GraphQL query.

## Technical Components
![entities](../figures/OBG-gen-generic-resolver.png "Generic resolver function")

## Example for Answering the query

![entities](../figures/OBG-gen-generic-resolver-example.png "Example")

* Example query (Get the university including the head of each department where the UniversityID is `u1').
```
    { 
        UniversityList(
          filter:{
            UniversityID:{
            _eq:"u1"}
          }){ 
          departments{
            head
          }
        } 
    } 
```


  

