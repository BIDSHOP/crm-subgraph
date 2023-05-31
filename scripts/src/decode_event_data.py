from eth_abi import decode
from hexbytes import HexBytes

# Paste event topics in order here, enclosed in quotes and separated by commas
EVENT_TOPIC_LIST = [

]

# Paste event data in order here, enclosed in quotes and separated by commas
EVENT_DATA_LIST = [

]

PLAYER_BID_EVENT_SIGNATURE_HASH = '0xa09dd32955694000e96fcafeba044b4dbd4850f23f8ab83a94833731fc9e947f'

## UNCOMMENT TO USE THE SAMPLE PROVIDED
## Data taken from https://polygonscan.com/tx/0x3ae683c332adf08772296ad4be2c78f2041b64ba962053e97f7a2dc8fc8a6f8d#eventlog (see event #106)

# EVENT_TOPIC_LIST = [
#     '0xa09dd32955694000e96fcafeba044b4dbd4850f23f8ab83a94833731fc9e947f',
#     '0x0000000000000000000000008f29e7a6ba1d50df0097087e851c0ce0a4edee18',
#     '0x0000000000000000000000000000000000000000000000000000000000000001',
#     '0x0000000000000000000000000000000000000000000000000000000000000003'
# ]

# EVENT_DATA_LIST = [
#     '0000000000000000000000000000000000000000000000000000000000000001',
#     '0000000000000000000000000000000000000000000000000000000000000007',
#     '00000000000000000000000000000000000000000000000000000000000000c0',
#     '8265aee6614adb93770f52286029f73e69239d597df5199189c50887bd74eef9',
#     '0000000000000000000000000000000000000000000000000000000000000001',
#     '0000000000000000000000000000000000000000000000000000000000000000',
#     '0000000000000000000000000000000000000000000000000000000000000054',
#     '6537336530323935386339636161626534323338306363366333643263646266',
#     '6564313063366138646136646436633562373236666362376131326230346132',
#     '3633353833306139656363663533383336663436000000000000000000000000'
# ]

def get_topic_types(event_signature_hash: str) -> dict:
    try:
        if event_signature_hash == PLAYER_BID_EVENT_SIGNATURE_HASH:
            return {
                'bidder': 'address',
                'bidListId': 'uint256',
                'roundId': 'uint256'
            }
    except Exception as e:
        print(f'Error getting event topic types: {e}')
        raise e

def get_data_types(event_signature_hash: str):
    try:
        if event_signature_hash == PLAYER_BID_EVENT_SIGNATURE_HASH:
            return {
                'isBonus': 'bool',
                'poolId': 'uint256',
                'bidId': 'uint256',
                'hash': 'bytes32',
                'minValuedBidReached': 'bool',
                'cipher': 'string',
            }
    except Exception as e:
        print(f'Error getting event data types: {e}')
        raise e

if __name__ == '__main__':
    if EVENT_TOPIC_LIST[0] == PLAYER_BID_EVENT_SIGNATURE_HASH:
        EVENT_DATA_LIST = EVENT_DATA_LIST[0:5] + [EVENT_DATA_LIST[7] + EVENT_DATA_LIST[8] + EVENT_DATA_LIST[9]]
    else:
        raise Exception('Invalid 0th event topic')
    
    decoded_output = {}

    topic_types = get_topic_types(EVENT_TOPIC_LIST[0])

    for (topic_name, topic_type), topic in zip(topic_types.items(), EVENT_TOPIC_LIST[1:]):
        if topic_type == 'address':
            decoded = '0x' + topic[26:]
        elif topic_type == 'uint256':
            decoded = int(topic, 0)
        else:
            raise Exception('Unsupported data type')

        decoded_output[topic_name] = decoded
    
    data_types = get_data_types(EVENT_TOPIC_LIST[0])

    for (data_name, data_type), data in zip(data_types.items(), EVENT_DATA_LIST):
        if data_type in ['bool', 'uint256']:
            decoded = decode([data_type], HexBytes(data))[0]
        elif data_type == 'bytes32':
            decoded = data
        elif data_type == 'string':
            decoded = HexBytes(data).decode()
        else:
            raise Exception('Unsupported data type')
        
        decoded_output[data_name] = decoded
    
    print('Decoded event data')
    print()

    for (key, value) in decoded_output.items():
        print(f'{key}: {value}')