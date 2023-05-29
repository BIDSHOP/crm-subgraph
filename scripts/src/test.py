from time import sleep
import requests

SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/spencermiller23/bidshop-crm-mainnet'
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

def count_bids() -> dict:
    try:
        bid_count = 0
        last_id = ''

        while True:
            query = '''
                {
                    bids(first: %d, where: {id_gt: "%s"}) {
                        id
                    }
                }
            ''' % (MAX_RESPONSE_SIZE, last_id)

            res = query_subgraph(query)
            res = res['bids']

            bid_count += len(res)

            if len(res) < MAX_RESPONSE_SIZE:
                break

            last_id = res[-1]['id']
        
        return bid_count
    except Exception as e:
        print(f'Error getting bid count: {e}')
        raise e

if __name__ == '__main__':
    print(count_bids())