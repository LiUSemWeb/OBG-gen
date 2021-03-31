### Queries for Evaluation 

    query Query1{
      SpaceGroupList{
        SpaceGroupID
      }
    }

    query Query2{
      SpaceGroupList{
        SpaceGroupID
        SpaceGroupSymbol
      }
    }

    query Query3{
      StructureList{
        hasSpaceGroup{
          SpaceGroupID
          SpaceGroupSymbol
        }
      }
    }

    query Query4{
      StructureList{
        hasSpaceGroup{
          SpaceGroupID
          SpaceGroupSymbol
        }
        hasComposition{
          ReducedFormula
        }
      }
    }

    query Query5{
      CalculationList{
        hasOutputStructure{
          hasSpaceGroup{
            SpaceGroupID
            SpaceGroupSymbol
          }
        }
      }
    }

    query Query6{
      CalculationList{
        ID
        hasOutputStructure{
          hasSpaceGroup{
            SpaceGroupID
            SpaceGroupSymbol
          }
        }
      }
    }


