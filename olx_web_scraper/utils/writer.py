import csv

def data_to_csv(filename, data):
    with open(f'{filename}.csv', 'w', newline='', encoding="utf-8") as file: 
        writer = csv.writer(file)
        headers = ['Ad ID','Price','Model Year', 'KMS Driven', 'Ad Title', 'Ad Location', 'Ad Link']
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)