

### Real Case Evaluation

* An example query without filter expression is shown below. (List all structures including reduced formula.)
```
    {
        StructureList{
            hasComposition{
                ReducedFormula
            }
        }
    }
```

* An example query with filter expression is shown below. (List all calculations including ID, output calculated property name and value, where ID in a given list of values.)
``` 
    {
      CalculationList(
        filter: { ID: { _in: ["6332", "8088", "21331", "mp-561628", "mp-614918"] } }
      ) {
        ID
        hasOutputCalculatedProperty {
          PropertyName
          numericalValue
        }
      }
    }
```

* You can find all the 12 queries at [this folder](./materials_design_domain/OBG-gen).
* OBG-gen-rdb
* OBG-gen-mix
* morph-rdb
* HyperGraphQL
* UltraGraphQL

* Query Execution Time (QET) per data size on materials dataset.
![entities](../figures/evaluation-md-QETs-per-dataset.png "per-dataset")
* Query Execution Time (QET) per query on materials dataset.
![entities](../figures/evaluation-md-QETs-per-query.png "The framework of OBG-gen")

### Synthetic Evaluation

* An example query is shown below.
```
    { 
      UniversityList (filter:{nr:{_eq:973}}) { 
        undergraduateDegreeObtainedBystudent{ 
          advisor { 
            worksFor{nr} 
          } 
        } 
      } 
    } 
```
* You can find all the 8 query sets at [this folder](./university_domain_LinGBM).
* OBG-gen-rdb