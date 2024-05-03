from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_address

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract = w3.eth.contract(address=contract_address, abi=abi)

print (contract.address)

print(f"Баланс смарт контракта: {w3.eth.get_balance(contract.address)}")
print(f"Баланс первого аккаунта: {w3.eth.get_balance('0x8B2279c3b75E80E14F3B80a730001D9472bc1839')}")
print(f"Баланс второго аккаунта: {w3.eth.get_balance('0x2567331EDA591A75eFef45f49c7A3AeE10a80De0')}")
print(f"Баланс третьего аккаунта: {w3.eth.get_balance('0x6A821dAe555307209424dFeCB14a2145a4f18e55')}")
print(f"Баланс четвертого аккаунта: {w3.eth.get_balance('0x9EbA30f802e045378263b1A3D307A23A2D9000b0')}")
print(f"Баланс пятого аккаунта: {w3.eth.get_balance('0x42E8d90D5B3fc959c8664E57aEF30aC35c95b706')}")