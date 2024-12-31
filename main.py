import csv
import os
import sys
from decimal import Decimal

def map_account(type, tags, account):
    if type == "Expense":
        return f"Expenses:{tags}" if tags else "Expenses:Miscellaneous"
    elif type == "Refund":
        return f"Expenses:{tags}" if tags else "Expenses:Miscellaneous"  # Refunds treated as Expenses
    elif type == "Settlement":
        return "Liabilities:Settlements"
    elif type == "Loan":
        return "Liabilities:Loans"
    elif type == "Transfer":
        return f"Assets:{account}" if account else "Assets:Unknown"
    else:
        return "Unknown"

def convert_csv_to_ledger(input_csv):
    output_ledger = os.path.join(os.getcwd(), "transactions.ledger")

    with open(input_csv, "r", encoding="utf-16") as csvfile, open(output_ledger, "w", encoding="utf-8") as ledgerfile:
        reader = csv.DictReader(csvfile, delimiter="\t")

        for row in reader:
            date = row["Date"].strip()
            description = row["Description"].strip()
            currency = row["Currency"].strip()
            amount = Decimal(row["Amount"].strip())
            type = row["Type"].strip()
            tags = row["Tags"].strip()
            account = row["Account"].strip()
            status = row["Status"].strip()
            memo = row["Memo"].strip()

            if type == "Expense":  # Expenses
                debit_account = map_account(type, tags, account)
                credit_account = f"Assets:{account}"
                debit_amount = -amount
                credit_amount = amount
            elif type == "Refund":  # Refunds
                debit_account = f"Assets:{account}"  # Assets is positive
                credit_account = map_account(type, tags, account)  # Refund as negative expense
                debit_amount = amount
                credit_amount = -amount
            # elif "Bankomacie" in description:  # Check if the description indicates ATM withdrawal
            #     debit_account = "Assets:Portfel"  # Money goes to the wallet
            #     credit_account = f"Assets:{account}" if account else "Assets:Unknown"  # Money comes from the bank account
            #     debit_amount = -amount
            #     credit_amount = amount
            elif type == "Transfer":  # Transfers
                source_account = f"Assets:{tags}" if tags else "Assets:Unknown"  # From (negative)
                destination_account = f"Assets:{account}"  # To (positive)
                debit_account = destination_account
                credit_account = source_account
                debit_amount = amount
                credit_amount = -amount
            else: 
                debit_account = map_account(type, tags, account)
                credit_account = f"Assets:{account}"
                debit_amount = -amount
                credit_amount = amount

            ledgerfile.write(f"{date} * {description}\n")
            ledgerfile.write(f"    {debit_account:<30} {debit_amount:.2f} {currency}\n")
            ledgerfile.write(f"    {credit_account:<30} {credit_amount:.2f} {currency}\n")

            if memo:
                ledgerfile.write(f"    ; Memo: {memo}\n")

            ledgerfile.write("\n")

    print(f"Conversion completed. Ledger file saved as {output_ledger}.")

if __name__ == "__main__":
    input_file = sys.argv[1]
    convert_csv_to_ledger(input_file)