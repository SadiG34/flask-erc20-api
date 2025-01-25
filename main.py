import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from web3 import Web3

load_dotenv()
app = Flask(__name__)
api_key = os.getenv('api_key')
api_key_infura = os.getenv('api_key_infura')

w3 = Web3(Web3.HTTPProvider(f'https://polygon-mainnet.infura.io/v3/{api_key_infura}'))

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "payable": True,
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]


def get_balance(api_key, address):
    url = 'https://api.polygonscan.com/api'
    params = {
        "module": 'account',
        "action": 'balance',
        "address": address,
        "apikey": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        balance_data = response.json()
        if 'result' in balance_data:
            return balance_data['result']
        else:
            return {"error": f"Error in response: {balance_data}"}
    else:
        return {"error": f"Failed to fetch data for {address}: {response.status_code}"}


def get_erc20_balance(token_address, user_address, abi):
    infura_url = f'https://polygon-mainnet.infura.io/v3/{api_key_infura}'
    web3 = Web3(Web3.HTTPProvider(infura_url))
    contract = web3.eth.contract(address=Web3.to_checksum_address(token_address.lower()), abi=abi)
    balance = contract.functions.balanceOf(Web3.to_checksum_address(user_address.lower())).call()

    return balance


@app.route('/get_balance', methods=['GET'])
def api_get_balance():
    address = request.args.get('address')

    if address:
        balance = get_balance(api_key, address)
        return jsonify({"balance": balance})
    else:
        return jsonify({"error": "Address parameter is required."}), 400


@app.route('/get_erc20_balance', methods=['GET'])
def api_get_erc20_balance():
    token_address = request.args.get('token_address')
    user_address = request.args.get('user_address')

    if token_address and user_address:
        balance = get_erc20_balance(token_address, user_address, ERC20_ABI)
        return jsonify({"balance": balance})
    else:
        return jsonify({"error": "Token address and user address parameters are required."}), 400


@app.route('/get_balance_batch', methods=['POST'])
def api_get_balance_batch():
    data = request.get_json()

    if not data or 'addresses' not in data:
        return jsonify({"error": "Addresses parameter is required."}), 400

    addresses = data['addresses']
    balances = []

    for address in addresses:
        balance = get_balance(api_key, address)
        balances.append(balance)

    return jsonify({"balances": balances})


if __name__ == "__main__":
    app.run(host='localhost', port=8080)

# POST http://localhost:8080/get_balance_batch
#   Body: {"addresses": ["0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d", "0x4830AF4aB9cd9E381602aE50f71AE481a7727f7C"]}
#
# GET http://localhost:8080/get_balance?address=0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d
# http://localhost:8080/get_erc20_balance?token_address=0xTokenAddress&user_address=UserAddress
