import garth
import os

email = os.getenv('GARMIN_USER')
password = os.getenv('GARMIN_PASS')

# garth.login(email, password)
# garth.save("~/.garth")

garth.resume("~/.garth")

try:
    garth.client.username
    print("Logged in as", garth.client.username)
except GarthException:
    # Session is expired. You'll need to log in again
    print("Session is expired. You'll need to log in again")

while True:
    endpoint = input("Enter an endpoint: ")
    if endpoint == "exit":
        break
    else:
        result = garth.connectapi(endpoint)
        print(result)


