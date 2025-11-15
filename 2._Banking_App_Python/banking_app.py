import csv
import os
from datetime import datetime

# --------------------------------------------
# Utility Functions
# --------------------------------------------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def create_file_if_missing(filename, fieldnames):
    """Creates CSV file with headers if not exists."""
    if not os.path.exists(filename):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


def read_csv(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    return data


def write_csv(filename, fieldnames, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


# --------------------------------------------
# OOP: Data Models
# --------------------------------------------
class BankAccount:
    def __init__(self, acc_no, cust_id, balance=0.0):
        self.acc_no = acc_no
        self.cust_id = cust_id
        self.balance = float(balance)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        print(f"{amount} deposited successfully. Balance: {self.balance}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        print(f"{amount} withdrawn successfully. Balance: {self.balance}")

    def to_dict(self):
        return {"AccountNo": self.acc_no, "CustomerID": self.cust_id, "Balance": self.balance}


class SavingsAccount(BankAccount):
    def __init__(self, acc_no, cust_id, balance=0.0, interest_rate=0.03):
        super().__init__(acc_no, cust_id, balance)
        self.interest_rate = interest_rate

    def add_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        print(f"Interest {interest:.2f} added. New balance: {self.balance:.2f}")


# --------------------------------------------
# Customer Model
# --------------------------------------------
class Customer:
    def __init__(self, cust_id, name, email, phone):
        self.cust_id = cust_id
        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self):
        return {"CustomerID": self.cust_id, "Name": self.name, "Email": self.email, "Phone": self.phone}


# --------------------------------------------
# Banking System Controller
# --------------------------------------------
class BankingSystem:
    def __init__(self):

        # CSV file locations
        base = os.path.dirname(os.path.abspath(__file__))
        self.customers_file = os.path.join(base, "customers.csv")
        self.accounts_file = os.path.join(base, "accounts.csv")
        self.transactions_file = os.path.join(base, "transactions.csv")

        # Auto-create CSV files if missing
        create_file_if_missing(self.customers_file, ["CustomerID", "Name", "Email", "Phone"])
        create_file_if_missing(self.accounts_file, ["AccountNo", "CustomerID", "Balance"])
        create_file_if_missing(self.transactions_file, ["Timestamp", "AccountNo", "Action", "Amount"])

        # Load data
        self.customers = read_csv(self.customers_file)
        self.accounts = read_csv(self.accounts_file)
        self.transactions = read_csv(self.transactions_file)

        print("Python Banking System Initialized.\n")
        print("CSV Folder:", base)

    # ---------- CUSTOMER OPS ----------
    def add_customer(self):
        cid = "C" + str(len(self.customers) + 1).zfill(3)

        name = input("Enter Customer Name: ").title()
        email = input("Enter Email: ")
        phone = input("Enter Phone: ")

        # Save customer
        customer = Customer(cid, name, email, phone).to_dict()
        self.customers.append(customer)
        write_csv(self.customers_file,
                  ["CustomerID", "Name", "Email", "Phone"], self.customers)

        print(f"Customer '{name}' added successfully with ID {cid}.")

        # Auto-create first account
        acc_no = "A" + str(len(self.accounts) + 1).zfill(4)
        new_acc = SavingsAccount(acc_no, cid, 0.0)

        self.accounts.append(new_acc.to_dict())
        write_csv(self.accounts_file,
                  ["AccountNo", "CustomerID", "Balance"], self.accounts)

        print("\nAccount Created Automatically")
        print("----------------------------")
        print(f"Account Number : {acc_no}")
        print(f"Customer ID    : {cid}")
        print("Initial Balance: 0.00\n")

    # ---------- VIEW CUSTOMERS ----------
    def view_customers(self):
        if not self.customers:
            print("No customers available.")
            return

        print("\n--- All Customers ---")
        for c in self.customers:
            print(f"{c['CustomerID']} | {c['Name']} | {c['Email']} | {c['Phone']}")

    # ---------- VIEW ACCOUNTS ----------
    def list_accounts(self):
        if not self.accounts:
            print("No accounts found.")
            return

        print("\n--- Accounts ---")
        for a in self.accounts:
            print(f"{a['AccountNo']} | {a['CustomerID']} | {float(a['Balance']):.2f}")

    # ---------- REMOVE ACCOUNT + REMOVE CUSTOMER ----------
    def remove_account(self):
        acc_no = input("Enter Account Number to remove: ").upper().strip()
        if not acc_no:
            print("No account number entered.")
            return

        # Find account
        account = next((a for a in self.accounts if a["AccountNo"] == acc_no), None)
        if not account:
            print("Account not found.")
            return

        cust_id = account["CustomerID"]

        confirm = input(
            f"Delete Account {acc_no} AND its Customer {cust_id}? (y/n): "
        ).lower().strip()

        if confirm != "y":
            print("Operation cancelled.")
            return

        # 1. Remove account
        self.accounts = [a for a in self.accounts if a["AccountNo"] != acc_no]
        write_csv(self.accounts_file,
                  ["AccountNo", "CustomerID", "Balance"], self.accounts)

        # 2. Remove customer
        self.customers = [c for c in self.customers if c["CustomerID"] != cust_id]
        write_csv(self.customers_file,
                  ["CustomerID", "Name", "Email", "Phone"], self.customers)

        # 3. Remove transactions
        self.transactions = [t for t in self.transactions if t["AccountNo"] != acc_no]
        write_csv(self.transactions_file,
                  ["Timestamp", "AccountNo", "Action", "Amount"], self.transactions)

        print(f"\nAccount {acc_no} and Customer {cust_id} deleted successfully.\n")

    # ---------- TRANSACTION OPS ----------
    def log_transaction(self, acc_no, action, amount):
        entry = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "AccountNo": acc_no,
            "Action": action,
            "Amount": amount
        }
        self.transactions.append(entry)
        write_csv(self.transactions_file,
                  ["Timestamp", "AccountNo", "Action", "Amount"], self.transactions)

    def transaction(self, action):
        acc_no = input("Enter Account Number: ").upper()

        acc = next((a for a in self.accounts if a["AccountNo"] == acc_no), None)
        if not acc:
            print("Account not found.")
            return

        account = SavingsAccount(acc_no, acc["CustomerID"], float(acc["Balance"]))

        try:
            amount = float(input("Enter Amount: "))

            if action == "deposit":
                account.deposit(amount)
            elif action == "withdraw":
                account.withdraw(amount)
            elif action == "interest":
                account.add_interest()
            else:
                print("Invalid action.")
                return

            # Update balance in CSV list
            for a in self.accounts:
                if a["AccountNo"] == acc_no:
                    a["Balance"] = account.balance

            write_csv(self.accounts_file,
                      ["AccountNo", "CustomerID", "Balance"], self.accounts)

            # Log transaction
            self.log_transaction(acc_no, action, amount)

        except ValueError as e:
            print(f"Error: {e}")

    # ---------- REPORTS ----------
    def show_reports(self):
        print("\n--- Banking Reports ---")

        if not self.accounts:
            print("No accounts found.")
            return

        total_balance = sum(float(a["Balance"]) for a in self.accounts)
        print(f"Total Bank Balance: {total_balance:.2f}")

        top_accounts = sorted(
            self.accounts, key=lambda x: float(x["Balance"]), reverse=True)[:3]

        print("\nTop 3 Balances:")
        for a in top_accounts:
            print(f"{a['AccountNo']} - {a['Balance']}")


# --------------------------------------------
# LOGIN SYSTEM
# --------------------------------------------
USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "teller": {"password": "teller@123", "role": "Teller"}
}


def login():
    print("\n===== LOGIN =====")
    username = input("Username: ").lower()
    password = input("Password: ")

    if username in USERS and USERS[username]["password"] == password:
        print(f"Logged in as {USERS[username]['role']}.")
        return USERS[username]["role"]

    print("Invalid credentials.")
    return None


# --------------------------------------------
# MAIN PROGRAM
# --------------------------------------------
def main():
    role = login()
    if not role:
        return

    system = BankingSystem()

    while True:
        print("\n===== MAIN MENU =====")
        print("1. Add Customer (Customer + Auto Account)")
        print("2. View Customers")
        print("3. View Accounts")
        print("4. Deposit")
        print("5. Withdraw")
        print("6. Add Interest")
        print("7. Reports")
        print("8. Remove Account (Deletes Customer Too)")
        print("9. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            system.add_customer()
        elif choice == "2":
            system.view_customers()
        elif choice == "3":
            system.list_accounts()
        elif choice == "4":
            system.transaction("deposit")
        elif choice == "5":
            system.transaction("withdraw")
        elif choice == "6":
            system.transaction("interest")
        elif choice == "7":
            system.show_reports()
        elif choice == "8":
            system.remove_account()
        elif choice == "9":
            print("Exiting system.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
