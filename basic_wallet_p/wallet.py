import sys
import os
import requests

def main():
    # get id
    f_path = os.path.join(os.path.dirname(__file__), '..', 'client_mining_p', 'my_id.txt')
    with open(f_path, 'r') as f:
        my_id = f.read()

    # get balance
    def get_balance():
        my_balance = 0
        my_transactions = []
        r = requests.get('http://localhost:5000/chain')
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)

        for block in data['chain']:
            for transaction in block['currentTransactions']:
                if transaction['sender'] == my_id:
                    my_balance -= transaction['amount']
                    my_transactions.append(transaction)
                elif transaction['recipient'] == my_id:
                    my_balance += transaction['amount']
                    my_transactions.append(transaction)
    
        my_transactions.reverse()
        return my_balance, my_transactions
    
    # ui
    def show_ui(page=1):
        print('Lambda Wallet')
        print('id:', my_id)
        print('balance:', my_balance)
        print(f'transactions (page {page}):')
        for transaction in my_transactions[(page-1)*10:(page-1)*10+10]:
            print(transaction)

    page = 1

    def command(cmd):
        nonlocal page
        nonlocal my_id
        commands = cmd.split(' ')
        # change id
        if commands[0] == 'id' and commands[1]:
            print('Changed id to:', commands[1])
            with open(f_path, 'w') as f:
                my_id = commands[1]
                f.write(commands[1])
        # change page
        elif commands[0] == 'page' and commands[1]:
            page = int(commands[1])
            if page < 1:
                page = 1
        elif commands[0] == 'quit':
            exit()
        else:
            print('Unrecognized command:', cmd)
            print('Valid commands:')
            print('    id <your-new-id>')
            print('    page <page-number>')
            print('    quit')

    while True:
        my_balance, my_transactions = get_balance()
        print()
        show_ui(page)
        print()
        cmd = input('Enter a command\n:')
        print()
        command(cmd)


if __name__ == "__main__":
    main()
