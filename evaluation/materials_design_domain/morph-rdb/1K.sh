
echo $1
properties_file_name="1K-$1.morph.properties"

cd ../..

echo $properties_file_name
#java -cp .:morph-rdb.jar:lib/*:dependency/* es.upm.fi.dia.oeg.morph.r2rml.rdb.engine.MorphRDBRunner examples-mysql/materials/1K 1K-q1-NF.morph.properties
time java -cp .:morph-rdb.jar:lib/*:dependency/* es.upm.fi.dia.oeg.morph.r2rml.rdb.engine.MorphRDBRunner examples-mysql/materials/1K $properties_file_name

cd examples-mysql/materials

