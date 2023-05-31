from time import sleep
import requests
import datetime
import csv

NETWORK = 'mainnet'
SUBGRAPH_URL = f'https://api.thegraph.com/subgraphs/name/spencermiller23/bidshop-crm-{NETWORK}'
MAX_RESPONSE_SIZE = 1000
MAX_RETRIES = 10

def get_auction_data() -> dict:
    try:
        auctions_dict = {}
        last_id = ''

        while True:
            query = '''
                {
                    auctions(first: %d, where: {id_gt: "%s"}) {
                        id
                        poolAddress
                        bidListId
                        startTime
                        endTime
                        bidsPlaced
                        totalPrizes
                    }
                }
            ''' % (MAX_RESPONSE_SIZE, last_id)

            res = query_subgraph(query)
            res = res['auctions']

            for auction in res:
                unique_bidders = get_unique_bidders(
                    auction['poolAddress'],
                    int(auction['bidListId'])
                )

                auction_winners = get_auction_winners(
                    auction['poolAddress'],
                    int(auction['bidListId'])
                )

                insert_auction(
                    auctions_dict,
                    auction['poolAddress'],
                    int(auction['bidListId']),
                    int(auction['startTime']),
                    int(auction['endTime']),
                    int(auction['totalPrizes']),
                    unique_bidders,
                    int(auction['bidsPlaced']),
                    auction_winners
                )

            if len(res) < MAX_RESPONSE_SIZE:
                break

            last_id = res[-1]['id']
        
        return auctions_dict
    except Exception as e:
        print(f'Error getting auction data: {e}')
        raise e

def get_unique_bidders(
    pool_address: str,
    bid_list_id: int
) -> int:
    try:
        unique_bidders = 0
        last_id = ''

        while True:
            query = '''
                {
                    bidlistPlayeds(first: %d, where: {pool_address: "%s", bidlist_id: "%d", id_gt: "%s"}) {
                        id
                    }
                }
            ''' % (MAX_RESPONSE_SIZE, pool_address, bid_list_id, last_id)

            res = query_subgraph(query)
            res = res['bidlistPlayeds']

            unique_bidders += len(res)

            if len(res) < MAX_RESPONSE_SIZE:
                break

            last_id = res[-1]['id']
        
        return unique_bidders
    except Exception as e:
        print(f'Error getting unique bidders: {e}')
        raise e

def get_auction_winners(
    pool_address: str,
    bid_list_id: int
) -> list:
    try:
        auction_winners = []

        query = '''
            {
                auctionWons(first: %d, where: {poolAddress: "%s", bidlistId: "%d"}) {
                    user
                }
            }
        ''' % (MAX_RESPONSE_SIZE, pool_address, bid_list_id)

        res = query_subgraph(query)

        for user in res['auctionWons']:
            if user not in auction_winners:
                auction_winners.append(user['user'])
    
        return auction_winners
    except Exception as e:
        print(f'Error getting auction winners: {e}')
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
    pool_address: str,
    bid_list_id: int,
    start_timestamp: int,
    end_timestamp: int,
    prize: int,
    unique_bidders: int,
    bids_placed: int,
    winners: list
) -> None:
    try:
        auction_id = f'{pool_address}-{bid_list_id}'
        
        if auction_id in auctions_dict.keys():
            return

        start_dt = datetime.datetime.fromtimestamp(start_timestamp, tz=datetime.timezone.utc)

        duration = (end_timestamp - start_timestamp) // (60 * 60)

        auctions_dict[auction_id] = {
            'start_date': f'{start_dt.month}/{start_dt.day}/{start_dt.year}',
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

def generate_csv(auctions_dict: dict) -> None:
    try:
        with open(f'./{NETWORK}_auctions.csv', 'w', encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator='\n')

            writer.writerow(['Auction ID', 'Start Date', 'Start Time', 'Duration', 'Total Prizes', 'Unique Bidders', 'Bids Placed', 'Winners'])

            for auction_id, data in auctions_dict.items():
                writer.writerow([auction_id, data['start_date'], data['start_time'], data['duration'], data['prize'] // (10 ** 18), data['unique_bidders'], data['bids_placed'], data['winners']])
    except Exception as e:
        print(f'Error generating csv file: {e}')
        raise e

if __name__ == '__main__':
    auctions_dict = get_auction_data()

    generate_csv(auctions_dict)
