
echo $1
properties_file_name="2K-$1.morph.properties"

cd ../..

echo $properties_file_name
#java -cp .:morph-rdb.jar:lib/*:dependency/* es.upm.fi.dia.oeg.morph.r2rml.rdb.engine.MorphRDBRunner examples-mysql/materials/2K 2K-q1-NF.morph.properties
java -cp .:morph-rdb.jar:lib/*:dependency/* es.upm.fi.dia.oeg.morph.r2rml.rdb.engine.MorphRDBRunner examples-mysql/materials/2K $properties_file_name

cd examples-mysql/materials

