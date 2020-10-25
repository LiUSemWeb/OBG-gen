from yaml import load, dump, FullLoader


#A = ['Calculation', 'Property', 'CalculatedProperty', 'PhysicalProperty', 'Structure', 'Quantity']
#V = ['xsd:string', 'xsd:double']
#U = ['ID', 'numericalValue', 'PropertyName']
#P = ['hasInputProperty', 'hasOutputProperty', 'hasInputStructure', 'hasOutputStructure', 'relatesToMaterial', 'relatesToStructure']
#subsumptions = [['CalculatedProperty', 'Property'], ['PhysicalProperty', 'Property']]
#assertions = [['Calculation', 'ID', 'xsd:string', '=1'], ['Calculation', 'hasInputStructure','Structure', '>=1']]
def read_TBox(TBox_file = './TBox.yml'):
    with open(TBox_file) as f:
        data = load(f, Loader=FullLoader)
        #print(data)
    return data['concepts'], data['data_types'], data['data_properties'], data['object_properties'], data['subsumptions'], data['axioms']
