import urllib.request
import urllib.error
try:
    req = urllib.request.Request('http://127.0.0.1:8000/register/')
    response = urllib.request.urlopen(req)
    print("Success:", response.getcode())
    print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"FAILED: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"OTHER ERROR: {e}")
