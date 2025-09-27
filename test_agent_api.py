"""
Test script for the MCP Agent API
"""
import asyncio
import httpx


async def test_agent_api():
    """Test the MCP Agent FastAPI endpoints"""
    base_url = "http://localhost:9001"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test root endpoint
            print("🧪 Testing root endpoint...")
            response = await client.get(f"{base_url}/")
            print(f"Root: {response.status_code} - {response.json()}")
            
            # Test health endpoint
            print("\n🩺 Testing health endpoint...")
            response = await client.get(f"{base_url}/api/v1/health")
            print(f"Health: {response.status_code} - {response.json()}")
            
            # Test status endpoint
            print("\n📊 Testing status endpoint...")
            response = await client.get(f"{base_url}/api/v1/status")
            print(f"Status: {response.status_code} - {response.json()}")
            
            # Test notebooks list
            print("\n📔 Testing notebooks list...")
            response = await client.get(f"{base_url}/api/v1/notebooks")
            print(f"Notebooks: {response.status_code} - {response.json()}")
            
        except Exception as e:
            print(f"❌ Error testing API: {e}")


if __name__ == "__main__":
    asyncio.run(test_agent_api())