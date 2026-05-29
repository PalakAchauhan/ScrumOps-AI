#!/usr/bin/env python
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

print("=" * 60)
print("SLACK CONNECTION DEBUG TEST")
print("=" * 60)

# Check if env vars are loaded
print(f"\n✓ SLACK_BOT_TOKEN loaded: {bool(SLACK_BOT_TOKEN)}")
print(f"  Token starts with: {SLACK_BOT_TOKEN[:20]}..." if SLACK_BOT_TOKEN else "  ✗ Not found")

print(f"\n✓ SLACK_SIGNING_SECRET loaded: {bool(SLACK_SIGNING_SECRET)}")
print(f"  Secret: {SLACK_SIGNING_SECRET}" if SLACK_SIGNING_SECRET else "  ✗ Not found")

if not SLACK_BOT_TOKEN:
    print("\n❌ SLACK_BOT_TOKEN not found in .env!")
    exit(1)

# Try to connect to Slack
print("\n" + "-" * 60)
print("Attempting Slack API connection...")
print("-" * 60)

try:
    client = WebClient(token=SLACK_BOT_TOKEN)
    
    # Test 1: Auth test
    print("\n📌 Test 1: Auth test")
    auth_result = client.auth_test()
    print(f"  ✓ Authentication successful!")
    print(f"  User ID: {auth_result.get('user_id')}")
    print(f"  Bot ID: {auth_result.get('bot_id')}")
    print(f"  Team: {auth_result.get('team_name')}")
    
    # Test 2: Team info (get team ID from auth_info)
    print("\n📌 Test 2: Get Team ID from auth_info")
    team_id = auth_result.get("team_id")
    print(f"  ✓ Team ID retrieved!")
    print(f"  Team ID: {team_id}")
    
    # Test 3: Get channels
    print("\n📌 Test 3: Get channels")
    channels_response = client.conversations_list(types="public_channel,private_channel", limit=3)
    channels = channels_response.get("channels", [])
    print(f"  ✓ Retrieved {len(channels)} channels")
    if channels:
        first_channel = channels[0]
        print(f"  First channel ID: {first_channel.get('id')}")
        print(f"  First channel name: {first_channel.get('name')}")
    
    # Build redirect URL
    team_id = auth_result.get("team_id")
    first_channel_id = channels[0].get("id") if channels else None
    
    print("\n" + "=" * 60)
    print("REDIRECT URL FOR HOMEPAGE:")
    print("=" * 60)
    if team_id and first_channel_id:
        redirect_url = f"https://app.slack.com/client/{team_id}/{first_channel_id}"
        print(f"\n✓ Your redirect URL should be:\n{redirect_url}\n")
    else:
        print(f"\n❌ Could not build URL. Team ID: {team_id}, Channel ID: {first_channel_id}\n")
    
    print("=" * 60)
    print("✅ SLACK CONNECTION TEST PASSED")
    print("=" * 60)
    
except SlackApiError as e:
    print(f"\n❌ Slack API Error: {e.response.get('error')}")
    print(f"   Details: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")
