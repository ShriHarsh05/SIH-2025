"""
Wait for Bahmni to be ready
Checks every 10 seconds until OpenMRS is fully initialized
"""

import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BAHMNI_URL = "http://localhost"
USERNAME = "superman"
PASSWORD = "Admin123"
MAX_WAIT = 600  # 10 minutes

print("=" * 70)
print("⏳ Waiting for Bahmni to be ready...")
print("=" * 70)
print("\nThis usually takes 5-10 minutes after starting containers.")
print("OpenMRS needs to initialize the database and load modules.\n")

start_time = time.time()
attempt = 0

while True:
    attempt += 1
    elapsed = int(time.time() - start_time)
    
    print(f"[{elapsed}s] Attempt {attempt}: Checking OpenMRS status...", end=" ")
    
    try:
        response = requests.get(
            f"{BAHMNI_URL}/openmrs/ws/rest/v1/session",
            auth=(USERNAME, PASSWORD),
            timeout=5,
            verify=False
        )
        
        if response.status_code == 200:
            print("✅ READY!")
            print("\n" + "=" * 70)
            print("🎉 Bahmni is fully initialized and ready!")
            print("=" * 70)
            print(f"\nTotal initialization time: {elapsed} seconds ({elapsed//60} minutes)")
            print(f"\n✅ You can now:")
            print(f"   1. Access Bahmni: http://localhost")
            print(f"   2. Use your application: http://localhost:8000")
            print(f"   3. Send conditions to EMR")
            print(f"\n🔑 Credentials:")
            print(f"   Bahmni: superman / Admin123")
            print(f"   Your App: demo@example.com / demo123")
            break
        else:
            print(f"⏳ Not ready yet (status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("⏳ OpenMRS not responding yet...")
    except requests.exceptions.Timeout:
        print("⏳ Connection timeout...")
    except Exception as e:
        print(f"⏳ Error: {str(e)[:50]}")
    
    if elapsed > MAX_WAIT:
        print(f"\n\n⚠️  Timeout after {MAX_WAIT} seconds")
        print("OpenMRS is taking longer than expected.")
        print("\nTroubleshooting:")
        print("1. Check container logs: docker compose logs openmrs")
        print("2. Check container status: docker compose ps")
        print("3. Restart if needed: docker compose restart")
        break
    
    time.sleep(10)  # Wait 10 seconds before next check

print("\n✨ Done!")
