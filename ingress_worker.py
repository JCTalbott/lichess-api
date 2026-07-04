import httpx
import json
import asyncio

async def get_elite_usernames(limit: int = 50) -> list:
    """Fetches the current top players in Blitz to isolate high ratings."""
    url = f"https://lichess.org/api/player/top/{limit}/blitz"
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Extract usernames from the leaderboard array
            return [user.get("username") for user in data.get("users", [])]
    return []

async def stream_user_history(client: httpx.AsyncClient, username: str):
    """Streams history for a single discovered user."""
    url = f"https://lichess.org/api/games/user/{username}"
    headers = {"Accept": "application/x-ndjson"}
    params = {
        "max": 100, # Small slice per player to prevent rate limits
        "moves": "true",
        "evals": "true",
        "pgnInJson": "true"
    }
    
    print(f"\n🚀 Launching history pipeline for Elite Player: {username}...")
    
    try:
        async with client.stream("GET", url, headers=headers, params=params) as response:
            count = 0
            async for line in response.aiter_lines():
                if line:
                    game_object = json.loads(line)
                    count += 1
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    print(game_object)
                    game_id = game_object.get("id")
                    w_rating = game_object.get("players", {}).get("white", {}).get("rating", 0)
                    b_rating = game_object.get("players", {}).get("black", {}).get("rating", 0)
                    
                    # Double-check our rating allowance filter criteria
                    if w_rating >= 2000 or b_rating >= 2000:
                        print(f"  [{count}] Saved Game {game_id} (White: {w_rating} vs Black: {b_rating})")
                        # --- BATCH INSERT TO POSTGRES / KAFKA PRODUCER RUNS HERE ---
                    
                    await asyncio.sleep(0.01)
                break
    except Exception as e:
        print(f"Error streaming {username}: {e}")

async def main():
    print("Scanning global leaderboards for target profiles...")
    elite_players = await get_elite_usernames(limit=5) # Grabs top 10 players dynamically
    print(f"Discovered targets: {elite_players}")
    
    # Share a single client across requests to reuse TCP connections efficiently
    async with httpx.AsyncClient(timeout=None) as client:
        for player in elite_players:
            await stream_user_history(client, player)
            # Polite pause between users to respect Lichess API rate boundaries
            await asyncio.sleep(2.0)

if __name__ == "__main__":
    asyncio.run(main())