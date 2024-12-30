# ledger-converter
Converter from .csv format file to .ledger file to use with Ledger CLI

## Usage: 

1. Enter path to yours .csv format file:
**Attention!** Do not enter path like `~/Downloads/something.csv` instead of this use:

MacOS: `/Users/user/Downloads/something.csv`

Windows: `C:\\Users\\User\\Downloads\\something.csv`

2. The script converts the CSV into a Ledger-compatible .ledger file in the current directory (transactions.ledger).
3. If you want to save .ledger file to custom directory then add the following to your code:

In function `def convert_csv_to_ledger(input_csv)`: `output_ledger = os.path.join(output_dir, "transactions.ledger")`

On the end of file: `output_dir = input("Enter the directory to save the Ledger file: ").strip()`


### Notes: 
The script maps the transaction types to Ledger accounts. You can customize the account mappings in the map_account function.

The script writes transactions with debit and credit entries, and includes a memo if provided.
