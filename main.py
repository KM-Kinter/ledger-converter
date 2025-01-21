import csv
import os
import sys
from dataclasses import dataclass
from decimal import Decimal


def map_account(type, tags, account):
    if type == "Expense":
        return (
            f"Expenses:{':'.join(tags.split(' / '))}"
            if tags
            else "Expenses:Miscellaneous"
        )
    elif type == "Income":
        return (
            f"Income:{':'.join(tags.split(' / '))}" if tags else "Income:Miscellaneous"
        )
    elif type == "Refund":
        return (
            f"Expenses:{':'.join(tags.split(' / '))}"
            if tags
            else "Expenses:Miscellaneous"
        )  # Refunds treated as Expenses
    elif type == "Settlement":
        return "Liabilities:Settlements"
    elif type == "Loan":
        return "Liabilities:Loans"
    elif type == "Transfer":
        return f"Assets:{account}" if account else "Assets:Unknown"
    else:
        return "Unknown"


class Transaction:
    def __init__(self, fields):
        self.date = fields.date
        self.description = fields.description
        self.currency = fields.currency
        self.memo = fields.memo

        if fields.type == "Expense":  # Expenses
            self.debit_account = map_account(fields.type, fields.tags, fields.account)
            self.credit_account = f"Assets:{fields.account}"
            self.debit_amount = -fields.amount
            self.credit_amount = fields.amount
        elif fields.type == "Refund":  # Refunds
            self.debit_account = f"Assets:{fields.account}"  # Assets is positive
            self.credit_account = map_account(
                fields.type, fields.tags, fields.account
            )  # Refund as negative expense
            self.debit_amount = fields.amount
            self.credit_amount = -fields.amount
        elif fields.type == "Transfer":  # Transfers
            source_account = (
                f"Assets:{fields.account}" if fields.amount > 0 else "Assets:Unknown"
            )  # From (negative)
            destination_account = (
                f"Assets:{fields.account}" if fields.amount < 0 else "Assets:Unknown"
            )  # To (positive)
            self.debit_account = destination_account
            self.credit_account = source_account
            self.debit_amount = fields.amount
            self.credit_amount = -fields.amount
        else:
            self.debit_account = map_account(fields.type, fields.tags, fields.account)
            self.credit_account = f"Assets:{fields.account}"
            self.debit_amount = -fields.amount
            self.credit_amount = fields.amount

    def add_missing(self, fields):
        if self.credit_account == "Assets:Unknown":
            self.credit_account = f"Assets:{fields.account}"
        if self.debit_account == "Assets:Unknown":
            self.debit_account = f"Assets:{fields.account}"

    def serialize(self, id, ledgerfile):
        ledgerfile.write(f"; ID: {id}\n")
        ledgerfile.write(f"{self.date} * {self.description}\n")
        ledgerfile.write(
            f"    {self.debit_account:<40} {self.debit_amount:.2f} {self.currency}\n"
        )
        ledgerfile.write(
            f"    {self.credit_account:<40} {self.credit_amount:.2f} {self.currency}\n"
        )

        if self.memo:
            memo = "\n;".join(self.memo.split("\n"))
            ledgerfile.write(f"    ; Memo: {memo}\n")

        ledgerfile.write("\n")


class Transactions:
    def __init__(self):
        self.transactions = {}

    def add(self, transaction_fields):
        if transaction_fields.id not in self.transactions:
            self.transactions[transaction_fields.id] = Transaction(transaction_fields)
        else:
            self.transactions[transaction_fields.id].add_missing(transaction_fields)

    def get_all(self):
        return self.transactions


class TransactionFields:
    def __init__(self, row):
        self.id = row["ID"].strip()
        self.date = row["Date"].strip()
        self.description = row["Description"].strip()
        self.currency = row["Currency"].strip()
        self.amount = Decimal(row["Amount"].strip())
        self.type = row["Type"].strip()
        self.tags = row["Tags"].strip()
        self.account = row["Account"].strip()
        self.status = row["Status"].strip()
        self.memo = row["Memo"].strip()


class Converter:
    def __init__(self, reader, ledgerfile):
        self.reader = reader
        self.ledgerfile = ledgerfile

    def process(self):
        transactions = Transactions()

        for row in self.reader:
            fields = TransactionFields(row)

            transactions.add(fields)

        for id, transaction in transactions.get_all().items():
            transaction.serialize(id, self.ledgerfile)


def convert_csv_to_ledger(input_csv):
    output_ledger = os.path.join(os.getcwd(), "transactions.ledger")

    with open(input_csv, "r", encoding="utf-16") as csvfile, open(
        output_ledger, "w", encoding="utf-8"
    ) as ledgerfile:
        reader = csv.DictReader(csvfile, delimiter="\t")

        converter = Converter(reader, ledgerfile)
        converter.process()

    print(f"Conversion completed. Ledger file saved as {output_ledger}.")


if __name__ == "__main__":
    input_file = sys.argv[1]
    convert_csv_to_ledger(input_file)

