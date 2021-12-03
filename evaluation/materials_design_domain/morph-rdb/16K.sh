
echo $1
properties_file_name="16K-$1.morph.properties"

cd ../..

echo $properties_file_name
#java -cp .:morph-rdb.jar:lib/*:dependency/* es.upm.fi.dia.oeg.morph.r2rml.rdb.engine.MorphRDBRunner examples-mysql/materials/16K 16K-q1-NF.morph.properties
java -cp .:morph-rdb.jar:lib/*:dependency/* es.upm.fi.dia.oeg.morph.r2rml.rdb.engine.MorphRDBRunner examples-mysql/materials/16K $properties_file_name

cd examples-mysql/materials

