import { Address, BigInt, Bytes } from "@graphprotocol/graph-ts";
import {
  PlayerBid as PlayerBidEvent, RoundFinalized, RoundFinalized1
} from "../generated/AuctionPool1/AuctionPool"
import { Auction, Bid, Platform, User } from "../generated/schema";

export function handlePlayerBid(event: PlayerBidEvent): void {
  if (isTeamWallet(event.params.bidder))
    return

  const platform = getPlatform()

  const auction = getAuction(event.address, event.params.bidListId)

  const user = getUser(platform, event.params.bidder, event.block.timestamp, event.transaction.hash)

  const bid = new Bid(`${event.address.toHexString()}-${event.params.poolId}-${event.params.bidListId}-${event.params.bidId}`)

  bid.poolAddress = event.address
  bid.bidListId = event.params.bidListId
  bid.bidId = event.params.bidId
  bid.bidder = event.params.bidder
  bid.timestamp = event.block.timestamp
  bid.txHash = event.transaction.hash

  bid.save()
}

export function handleRoundFinalized(event: RoundFinalized): void {
  const platform = getPlatform()

  platform.total_auctions_closed = platform.total_auctions_closed.plus(BigInt.fromI32(1))

  platform.save()
}

export function handleRankedRoundFinalized(event: RoundFinalized1): void {
  const platform = getPlatform()

  platform.total_auctions_closed = platform.total_auctions_closed.plus(BigInt.fromI32(1))

  platform.save()
}

function isTeamWallet(walletAddress: Address): bool {
  if (
    walletAddress.equals(Address.fromString('0x6292D674a4E8B3bF04B593A6D4723a5e06a9a0cE')) ||
    walletAddress.equals(Address.fromString('0x629ae6A17d2DFF9da257e1064cac96786991a475')) ||
    walletAddress.equals(Address.fromString('0x6A1CaaB803df63Bbe53e6729755e16bA05788905')) ||
    walletAddress.equals(Address.fromString('0x46EA7A7827D444ac3e9C9B8ef4601993D64Fc6Ab')) ||
    walletAddress.equals(Address.fromString('0x6F21E5239eDed4e654bB1208c5e32Cf04A869f34'))
  ) {
    return true
  }

  return false
}

function getPlatform(): Platform {
  let platform = Platform.load('platform')

  if (platform == null) {
    platform = new Platform('platform')

    platform.total_players = BigInt.fromI32(0)
    platform.total_bids_placed = BigInt.fromI32(0)
    platform.total_auctions_closed = BigInt.fromI32(0)
  }
  
  platform.total_bids_placed = platform.total_bids_placed.plus(BigInt.fromI32(1))
  
  platform.save()

  return platform
}

function getAuction(
  poolAddress: Address,
  bidListId: BigInt
): Auction {
  let auction = Auction.load(`${poolAddress.toHexString()}-${bidListId}`)

  if (auction == null) {
    auction = new Auction(`${poolAddress.toHexString()}-${bidListId}`)

    auction.poolAddress = poolAddress
    auction.bidListId = bidListId
    auction.bidsPlaced = BigInt.fromI32(0)
  }

  auction.bidsPlaced = auction.bidsPlaced.plus(BigInt.fromI32(1))

  auction.save()

  return auction
}

function getUser(
  platform: Platform,
  walletAddress: Address,
  timestamp: BigInt,
  txHash: Bytes
): User {
  let user = User.load(walletAddress)

  if (user == null) {
    user = new User(walletAddress)

    user.first_bid_timestamp = timestamp
    user.total_bids = BigInt.fromI32(0)

    platform.total_players = platform.total_players.plus(BigInt.fromI32(1))

    platform.save()
  }

  user.last_bid_timestamp = timestamp
  user.last_bid_tx_hash = txHash
  user.total_bids = user.total_bids.plus(BigInt.fromI32(1))

  user.save()

  return user
}