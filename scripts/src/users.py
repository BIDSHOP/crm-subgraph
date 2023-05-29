from database import session_maker, Social
from time import sleep
import requests
import csv

SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/bidshop/bidshop-beta'
MAX_RESPONSE_SIZE = 1000
MAX_RETRIES = 10

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

def get_user_data() -> dict:
    try:
        users_dict = {}
        last_id = '0x0000000000000000000000000000000000000000'

        while True:
            query = '''
                {
                    users(first: %d, where: {id_gt: "%s"}) {
                        id
                        auctions_played_count
                        total_bids
                        total_rewards
                    }
                }
            ''' % (MAX_RESPONSE_SIZE, last_id)

            res = query_subgraph(query)
            res = res['users']

            for user in res:
                if int(user['total_bids']) > 0:
                    auctions_won = get_auctions_won(user['id'])
                    
                    insert_user(users_dict, user['id'], int(user['auctions_played_count']), auctions_won, int(user['total_bids']), int(user['total_rewards']))

            if len(res) < MAX_RESPONSE_SIZE:
                break

            last_id = res[-1]['id']
        
        return users_dict
    except Exception as e:
        print(f'Error getting user data: {e}')
        raise e

def get_auctions_won(wallet_address: str) -> int:
    try:
        auctions_won = 0
        last_id = ''

        while True:
            query = '''
                {
                    auctionWons(first: %d, where: {user: "%s", id_gt: "%s"}) {
                        id
                    }
                }
            ''' % (MAX_RESPONSE_SIZE, wallet_address, last_id)

            res = query_subgraph(query)
            res = res['auctionWons']

            auctions_won += len(res)

            if len(res) < MAX_RESPONSE_SIZE:
                break

            last_id = res[-1]['id']
        
        return auctions_won
    except Exception as e:
        print(f'Error getting auctions won: {e}')
        raise e

def insert_user(
    users_dict: dict,
    wallet_address: str,
    auctions_played: int,
    auctions_won: int,
    bids_placed: int,
    total_winnings: int
) -> None:
    try:
        if wallet_address not in users_dict.keys():
            users_dict[wallet_address] = {
                'discord_username': get_discord_username(wallet_address),
                'auctions_played': 0,
                'auctions_won': 0,
                'bids_placed': 0,
                'total_winnings': 0
            }

        users_dict[wallet_address]['auctions_played'] += auctions_played
        users_dict[wallet_address]['auctions_won'] += auctions_won
        users_dict[wallet_address]['bids_placed'] += bids_placed
        users_dict[wallet_address]['total_winnings'] += total_winnings
    except Exception as e:
        print(f'Error inserting user: {e}')
        raise e

def get_discord_username(wallet_address: str) -> str:
    try:
        with session_maker() as session:
            social = session.query(Social).filter(
                Social.wallet_address == wallet_address,
                Social.social_type == 'discord'
            ).first()

            if social is None:
                return ''
            
            return social.username
    except Exception as e:
        print(f'Error getting discord username: {e}')
        raise e

def generate_csv(users_dict: dict) -> None:
    try:
        with open('./users.csv', 'w', encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator='\n')

            writer.writerow(['Wallet', 'Discord', 'Auctions Played', 'Auctions Won', 'Bids Placed', 'Average Bids Per Auction Played', 'Total Winnings'])

            for wallet_address, data in users_dict.items():
                writer.writerow([wallet_address, str(data['discord_username']), data['auctions_played'], data['auctions_won'], data['bids_placed'], data['bids_placed'] / data['auctions_played'], data['total_winnings'] // (10 ** 18)])
    except Exception as e:
        print(f'Error generating csv file: {e}')
        raise e

if __name__ == '__main__':
    users_dict = get_user_data()

    generate_csv(users_dict)