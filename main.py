import csv
import os

def map_account(type, tags, account):
    if type == "Expense":
        return f"Expenses:{tags}" if tags else "Expenses:Miscellaneous"
    elif type == "Refund":
        return f"Income:Refund {account}" if account else "Income:Refunds"
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
            amount = float(row["Amount"].strip())
            type = row["Type"].strip()
            tags = row["Tags"].strip()
            account = row["Account"].strip()
            status = row["Status"].strip()
            memo = row["Memo"].strip()

            if type in ["Expense", "Settlement", "Loan", "Transfer"]:  # Any type other than Income/Refund
                debit_account = map_account(type, tags, account)  # Debit (e.g., Expenses) is positive
                credit_account = f"Assets:{account}"  # Credit (e.g., Assets) is negative
                debit_amount = -amount
                credit_amount = amount
            elif type in ["Refund", "Income"]:  # Special handling for Income/Refund
                debit_account = f"Assets:{account}"  # Debit (e.g., Assets) is positive
                credit_account = map_account(type, tags, account)  # Credit (e.g., Income) is negative
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

input_csv = input("Enter the path to the CSV file: ").strip()
convert_csv_to_ledger(input_csv)