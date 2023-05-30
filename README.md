# CRM Subgraph

This repository contains separate subgraphs for both Testnet and Mainnet auctions.

- [Testnet Subgraph URL](https://thegraph.com/hosted-service/subgraph/spencermiller23/bidshop-crm-testnet)
- [Mainnet Subgraph URL](https://thegraph.com/hosted-service/subgraph/spencermiller23/bidshop-crm-mainnet)

## How to verify the data

### Option 1: Analyzing subgraph data

We can start to verify the subgraph data by inspecting the data in the Subgraph Playground. [Link to instructions](https://docs.google.com/document/d/1dVr5dz7e9TBF9TWUMKSVO36WmDGgdyie5lhp8jhlKwk/edit?usp=sharing)

### Option 2: Deploy new subgraph

Another way to verify the logic of the subgraph would be to analyze the code, deploy an identical subgraph and then compare the data between the two of them. We can start by looking at the `auction-pool.ts` file that is located in both the `/mainnet/src` or `/testnet/src` folders. Here we can see simple "event handlers" for each of the relevant events, which are "PlayerBid" and "RoundFinalized" (note that there are two versions of the RoundFinalized event).

- `handlePlayerBid`: This event handler increments the total number of bids placed, and then creates the appropriate Auction, User and Bid Entities as necessary, whenever a user places a bid.
- `handleRoundFinalized`: This event handler increments the total number of closed auctions when an auction of type 1 is closed.
- `handleRoundFinalized1`: This event handler increments the total number of closed auctions when an auction of type 2 is closed.

To deploy a subgraph, you must have a GitHub account and have NodeJS installed on your machine (version ^17 or earlier).

#### Steps for deploying the subgraph

1. Navigate to the [Create Subgraph](https://thegraph.com/hosted-service/subgraph/create?account=MDQ6VXNlcjE4NjkxMjM1) page
2. Sign in with GitHub
3. Fill in the form to and click "Create Subgraph"
4. Clone this repository
5. Install the subgraph CLI (`npm install -g @graphprotocol/graph-cli` or `yarn global add @graphprotocol/graph-cli`)
6. Copy and run the authentication command from the right column under "Deploy" (ex: `graph auth --product hosted-service <AUTH_TOKEN>`)
7. Move to the directory for the desired subgraph (either `/mainnet` or `/testnet`)
8. Copy and run the deployment command from the right column under "Deploy" (ex: `graph deploy --product hosted-service <GITHUB_USERNAME>/<SUBGRAPH_NAME>`)

[Link to The Graph docs for more information on deploying subgraphs](https://thegraph.com/docs/en/developing/creating-a-subgraph/)

### Option 3: Using transaction data

Finally, we might be interested in inspecting the data that the subgraph receives as input. To do this, we can take the transaction hash from any relevant transaction, and decrypt both the transaction inputs as well as the events emitted.

To inspect the transaction input data, we can start by querying the subgraph for some Bid entity, and paste the transaction hash into the search bar on the appropriate block scanner (ex: PolygonScan for Polygon Mainnet). Toward the bottom of the page, we can see a button that says "Click to See More", which will reveal the "Input Data" section. Copy the raw input data, and then paste it into the "Input Data" section [here](https://lab.miguelmota.com/ethereum-input-data-decoder/example/). The last thing we need to do is copy and paste the contract ABI into the "ABI" section, which we can grab from either the `/mainnet/abis` or `/testnet/abis`.

To inspect the data included in the events emitted by a transaction, we could navigate to the "Logs" tab of the Transaction Details page, and run the `decode_event_data.py` script provided in the `/scripts` folder to see the decoded event data. It is important to note that it is this data that is eventually passed into the subgraph event handler functions. Note that the PlayerBid events will have a 0th topic of `0xa09dd32955694000e96fcafeba044b4dbd4850f23f8ab83a94833731fc9e947f`.