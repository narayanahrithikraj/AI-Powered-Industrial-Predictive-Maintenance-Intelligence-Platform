import requests

BASE_URL = "http://localhost:8000"

def run_tests():
    print("🧪 Running Platform End-to-End API Integration Tests...\n")

    # 1. Root Endpoint Check
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200
    print("✅ Root API Health Check: PASSED")

    # 2. Authentication Test (Admin)
    admin_auth = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "admin@enterprise.com", "password": "secret"})
    assert admin_auth.status_code == 200
    print("✅ Admin Authentication: PASSED")

    # 3. Authentication Test (User)
    user_auth = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "user@enterprise.com", "password": "secret"})
    assert user_auth.status_code == 200
    print("✅ Operator Authentication: PASSED")

    # 4. Machine List (Admin View - All Machines)
    admin_machines = requests.get(f"{BASE_URL}/api/v1/machines?role=ADMIN").json()
    assert len(admin_machines) >= 4
    print(f"✅ Admin Machine Registry Query ({len(admin_machines)} assets retrieved): PASSED")

    # 5. Machine List (User View - Filtered Assigned Machines)
    user_machines = requests.get(f"{BASE_URL}/api/v1/machines?role=USER&user_email=user@enterprise.com").json()
    assert len(user_machines) < len(admin_machines)
    print(f"✅ Operator RBAC Machine Filtering ({len(user_machines)} assigned assets retrieved): PASSED")

    # 6. ML Live Telemetry & Inference Test
    m_id = user_machines[0]["id"]
    telemetry_res = requests.get(f"{BASE_URL}/api/v1/telemetry/{m_id}").json()
    assert "telemetry" in telemetry_res
    assert "prediction" in telemetry_res
    assert "shap_importance" in telemetry_res
    print(f"✅ Live Telemetry, XGBoost Inference & SHAP Breakdown for Machine ID {m_id}: PASSED")

    print("\n🎉 ALL PLATFORM TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n❌ Test Failure: {e}")