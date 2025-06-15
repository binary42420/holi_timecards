import asyncio
import websockets
import json
from datetime import datetime, timedelta

async def test_schedule_data():
    """Test the schedule data retrieval functionality with login"""
    uri = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")

            # Step 1: Login first
            login_request = {
                "request_id": 10,
                "data": {
                    "username": "manager",  # Test manager user
                    "password": "password"  # Test manager password
                }
            }

            print("🔐 Attempting login...")
            await websocket.send(json.dumps(login_request))

            # Wait for login response
            login_response = await websocket.recv()
            login_data = json.loads(login_response)

            print(f"📥 Login response: {json.dumps(login_data, indent=2)}")

            if not login_data.get('data', {}).get('user_exists'):
                print("❌ Login failed - user doesn't exist or wrong credentials")
                return

            print("✅ Login successful!")

            # Step 2: Now request schedule data
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            schedule_request = {
                "request_id": 2001,
                "data": {
                    "start_date": start_of_week.isoformat(),
                    "end_date": end_of_week.isoformat(),
                    "view_type": "week",
                    "include_workers": True,
                    "include_jobs": True,
                    "include_clients": True,
                    "filters": {}
                }
            }

            print(f"📤 Sending schedule request: {json.dumps(schedule_request, indent=2)}")

            # Send the schedule request
            await websocket.send(json.dumps(schedule_request))

            # Wait for schedule response
            schedule_response = await websocket.recv()
            schedule_data = json.loads(schedule_response)

            print(f"📥 Schedule response: {json.dumps(schedule_data, indent=2)}")

            if schedule_data.get('success'):
                print("✅ Schedule data retrieved successfully!")
                shifts = schedule_data.get('data', {}).get('shifts', [])
                workers = schedule_data.get('data', {}).get('workers', [])
                jobs = schedule_data.get('data', {}).get('jobs', [])
                clients = schedule_data.get('data', {}).get('clients', [])

                print(f"📊 Found {len(shifts)} shifts")
                print(f"👥 Found {len(workers)} workers")
                print(f"💼 Found {len(jobs)} jobs")
                print(f"🏢 Found {len(clients)} clients")

                for shift in shifts:
                    print(f"   - Shift ID: {shift.get('id')}, Job ID: {shift.get('job_id')}")
            else:
                print(f"❌ Failed to retrieve schedule data: {schedule_data.get('error')}")

    except Exception as e:
        print(f"❌ Error connecting to server: {e}")

if __name__ == "__main__":
    asyncio.run(test_schedule_data())
