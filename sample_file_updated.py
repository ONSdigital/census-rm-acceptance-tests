import argparse
import csv

FIELDNAMES = ('ARID', 'ESTAB_ARID', 'UPRN', 'ADDRESS_TYPE', 'ESTAB_TYPE', 'ADDRESS_LEVEL', 'ABP_CODE',
              'ORGANISATION_NAME', 'ADDRESS_LINE1', 'ADDRESS_LINE2', 'ADDRESS_LINE3',
              'TOWN_NAME', 'POSTCODE', 'LATITUDE', 'LONGITUDE', 'OA', 'LSOA',
              'MSOA', 'LAD', 'REGION', 'HTC_WILLINGNESS', 'HTC_DIGITAL', 'TREATMENT_CODE',
              'FIELDCOORDINATOR_ID', 'FIELDOFFICER_ID', 'CE_EXPECTED_CAPACITY', 'CE_SECURE')


def main():
    parser = argparse.ArgumentParser(description='Fix sample file for new format')
    parser.add_argument('samplefile', help='the sample file', type=str)
    args = parser.parse_args()

    with open(args.samplefile, "r") as sample_file:
        sample_file_reader = csv.DictReader(sample_file, delimiter=',')
        with open(f'{args.samplefile}.new', 'w', newline='') as new_sample_file:
            write_new_file(new_sample_file, sample_file_reader)


def write_new_file(new_sample_file, sample_file_reader):
    writer = csv.DictWriter(new_sample_file, fieldnames=FIELDNAMES)
    writer.writeheader()
    new_row = dict()
    for row in sample_file_reader:
        for column in FIELDNAMES:
            if column == 'CE_SECURE':
                new_row['CE_SECURE'] = 0
            else:
                new_row[column] = row[column]

        writer.writerow(new_row)


if __name__ == "__main__":
    main()
