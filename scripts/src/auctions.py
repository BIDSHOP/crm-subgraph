from time import sleep
import requests
import datetime
import csv

SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/bidshop/bidshop-beta'
MAX_RESPONSE_SIZE = 1000
MAX_RETRIES = 10

def get_auction_data() -> dict:
    try:
        auctions_dict = {}
        last_id = ''

        while True:
            query = '''
                {
                    auctionBidLists(first: %d, where: {id_gt: "%s"}) {
                        id
                        chainId
                        factoryAddress
                        poolId
                        bidListId
                        startTime
                        endTime
                        bidsPlaced
                        totalPrizes
                    }
                }
            ''' % (MAX_RESPONSE_SIZE, last_id)

            res = query_subgraph(query)
            res = res['auctionBidLists']

            for auction in res:
                insert_auction(
                    auctions_dict,
                    int(auction['chainId']),
                    auction['factoryAddress'],
                    int(auction['poolId']),
                    int(auction['bidListId']),
                    int(auction['startTime']),
                    int(auction['endTime']),
                    int(auction['totalPrizes']),
                    0,
                    int(auction['bidsPlaced']),
                    []
                )

            if len(res) < MAX_RESPONSE_SIZE:
                break

            last_id = res[-1]['id']
        
        return auctions_dict
    except Exception as e:
        print(f'Error getting auction data: {e}')
        raise e

def get_unique_bidders(
    chain_id: int,
    factory_address: str,
    pool_id: int,
    bid_list_id: int
) -> int:
    try:
        unique_bidders = 0
        last_user = '0x0000000000000000000000000000000000000000'

        while True:
            query = '''
                {
                    bidListPlayeds(first: %d, where: {chainId: "%d", factoryAddress: "%s", poolId: "%d", bidListId: "%d", user_gt: "%s"}) {
                        id
                    }
                }
            ''' % (MAX_RESPONSE_SIZE, chain_id, factory_address, pool_id, bid_list_id, last_user)

            res = query_subgraph(query)
            res = res['bidListPlayeds']

            unique_bidders += len(res)

            if len(res) < MAX_RESPONSE_SIZE:
                break

            last_user = res[-1]['user']
        
        return unique_bidders
    except Exception as e:
        print(f'Error getting unique bidders: {e}')
        raise e

def query_subgraph(query: str) -> dict:
    for _ in range(MAX_RETRIES):
        try:
            res = requests.post(SUBGRAPH_URL, '', json={ 'query': query })

            if res.status_code != 200:
                raise Exception(res.status_code)
            
            print(res.json())
            
            return res.json()['data']
        except Exception as e:
            print(f'Error querying subgraph: {e}')
            sleep(20)
            print('Retrying...')

    raise Exception('Error querying subgraph')

def insert_auction(
    auctions_dict: dict,
    chain_id: int,
    factory_address: str,
    pool_id: int,
    bid_list_id: int,
    start_timestamp: int,
    end_timestamp: int,
    prize: int,
    unique_bidders: int,
    bids_placed: int,
    winners: list
) -> None:
    try:
        auction_id = f'{chain_id}-{factory_address}-{pool_id}-{bid_list_id}'
        
        if auction_id in auctions_dict.keys():
            return

        start_dt = datetime.datetime.fromtimestamp(start_timestamp, tz=datetime.timezone.utc)

        duration = (end_timestamp - start_timestamp) // (60 * 60)

        auctions_dict[auction_id] = {
            'start_date': f'{start_dt.day}/{start_dt.month}/{start_dt.year}',
            'start_time': f'{start_dt.hour}:{start_dt.minute}:{start_dt.second}',
            'duration': duration,
            'prize': prize,
            'unique_bidders': unique_bidders,
            'bids_placed': bids_placed,
            'winners': winners
        }
    except Exception as e:
        print(f'Error inserting auction: {e}')
        raise e

if __name__ == '__main__':
    auctions_dict = get_auction_data()

    print(auctions_dict)
    print(len(auctions_dict))