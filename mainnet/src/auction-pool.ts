import { Address, BigInt, Bytes } from "@graphprotocol/graph-ts";
import {
  AuctionPool,
  PlayerBid as PlayerBidEvent,
  RankRevealed,
  RoundFinalized,
  RoundFinalized1
} from "../generated/AuctionPool1/AuctionPool"
import {
  Auction,
  AuctionWon,
  Bid,
  BidlistPlayed,
  Platform,
  RankRevealedEvent,
  User
} from "../generated/schema";

export function handlePlayerBid(event: PlayerBidEvent): void {
  if (isTeamWallet(event.params.bidder))
    return

  const platform = getPlatform()

  const auction = getAuction(event.address, event.params.bidListId, event.block.timestamp)

  const user = getUser(platform, event.params.bidder, event.block.timestamp, event.transaction.hash)

  const bid = new Bid(`${event.address.toHexString()}-${event.params.poolId}-${event.params.bidListId}-${event.params.bidId}`)

  bid.poolAddress = event.address
  bid.bidListId = event.params.bidListId
  bid.bidId = event.params.bidId
  bid.bidder = event.params.bidder
  bid.timestamp = event.block.timestamp
  bid.txHash = event.transaction.hash

  bid.save()

  const bidListPlayed = getBidListPlayed(
    user,
    event.address,
    event.params.bidListId,
    event.params.bidder
  )
}

export function handleRoundFinalized(event: RoundFinalized1): void {
  const platform = getPlatform()

  platform.total_auctions_closed = platform.total_auctions_closed.plus(BigInt.fromI32(1))

  platform.save()

  const auctionWon = new AuctionWon(event.transaction.hash.toHex() + "-" + event.logIndex.toString())

  auctionWon.poolAddress = event.address
  auctionWon.bidlistId = event.params.bidListId
  auctionWon.roundId = event.params.roundId
  auctionWon.rank = BigInt.fromI32(1)
  auctionWon.reward = BigInt.fromI32(0)
  auctionWon.user = event.params.winner

  auctionWon.save()
}

export function handleRankRevealed(event: RankRevealed): void {
  const rankRevealedEntity = new RankRevealedEvent(`${event.transaction.hash.toHexString()}-${event.logIndex}`)

  rankRevealedEntity.bidListId = event.params.bidListId
  rankRevealedEntity.poolAddress = event.address
  rankRevealedEntity.rank = event.params.rank
  rankRevealedEntity.reward = event.params.reward
  rankRevealedEntity.roundId = event.params.roundId
  rankRevealedEntity.user = event.params.user

  rankRevealedEntity.save()

  let user = User.load(event.params.user)
  
  if (user == null)
    return
  
  user.total_rewards = user.total_rewards.plus(event.params.reward)

  user.save()

  let auction = Auction.load(`${event.address.toHexString()}-${event.params.bidListId}`)

  if (auction == null)
    return

  auction.totalPrizes = auction.totalPrizes.plus(event.params.reward)
  
  auction.save()

  const auctionWon = new AuctionWon(event.transaction.hash.toHex() + "-" + event.logIndex.toString())

  auctionWon.poolAddress = event.address
  auctionWon.bidlistId = event.params.bidListId
  auctionWon.roundId = event.params.roundId
  auctionWon.rank = event.params.rank
  auctionWon.reward = event.params.reward
  auctionWon.user = event.params.user

  auctionWon.save()
}

export function handleRankedRoundFinalized(event: RoundFinalized): void {
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
    platform.factories = BigInt.fromI32(0)
  }
  
  platform.total_bids_placed = platform.total_bids_placed.plus(BigInt.fromI32(1))
  
  platform.save()

  return platform
}

function getAuction(
  poolAddress: Address,
  bidListId: BigInt,
  startTime: BigInt
): Auction {
  let auction = Auction.load(`${poolAddress.toHexString()}-${bidListId}`)

  if (auction == null) {
    auction = new Auction(`${poolAddress.toHexString()}-${bidListId}`)

    auction.poolAddress = poolAddress
    auction.bidListId = bidListId
    auction.bidsPlaced = BigInt.fromI32(0)
    auction.startTime = startTime

    const roundDuration = getRoundDuration(poolAddress)

    auction.endTime = auction.startTime.plus(roundDuration)
    auction.totalPrizes = BigInt.fromI32(0)
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
    user.auctions_played_count = BigInt.fromI32(0)
    user.total_rewards = BigInt.fromI32(0)

    platform.total_players = platform.total_players.plus(BigInt.fromI32(1))

    platform.save()
  }

  user.last_bid_timestamp = timestamp
  user.last_bid_tx_hash = txHash
  user.total_bids = user.total_bids.plus(BigInt.fromI32(1))

  user.save()

  return user
}

function getBidListPlayed(
  user: User,
  poolAddress: Address,
  bidListId: BigInt,
  walletAddress: Address
): BidlistPlayed {
  const bidListPlayedId = `${poolAddress.toHexString()}-${bidListId}-${walletAddress.toHexString()}`

  let bidListPlayed = BidlistPlayed.load(bidListPlayedId)

  if (bidListPlayed == null) {
    user.auctions_played_count = user.auctions_played_count.plus(BigInt.fromI32(1))

    user.save()

    bidListPlayed = new BidlistPlayed(bidListPlayedId)

    bidListPlayed.user = walletAddress
    bidListPlayed.pool_address = poolAddress
    bidListPlayed.bidlist_id = bidListId
  }

  bidListPlayed.save()

  return bidListPlayed
}

function getRoundDuration(poolAddress: Address): BigInt {
  const auctionPoolContract = AuctionPool.bind(poolAddress)

  const roundDuration = auctionPoolContract.try_roundDuration()
  
  if (!roundDuration.reverted) {
    return roundDuration.value
  } else {
    return BigInt.fromI32(0)
  }
}