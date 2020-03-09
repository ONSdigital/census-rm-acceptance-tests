for csv_file in $(find . -name "*.csv")
do
  if grep -q "ARID,ESTAB_ARID,UPRN,ADDRESS_TYPE,ESTAB_TYPE,ADDRESS_LEVEL,ABP_CODE,ORGANISATION_NAME" $csv_file; then

    # Add extra column to CSV file with .new extension
    python sample_file_updated.py $csv_file

    # Remove old CSV file missing the extra column
    rm $csv_file

    # Replace the old CSV file with the new CSV file
    mv $csv_file.new $csv_file

    echo Added extra column to $csv_file
  else
    echo Ignoring $csv_file
  fi
done