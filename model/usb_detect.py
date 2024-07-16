import time
import pychromecast

def detect_chromecast():
    while True:
        print("Searching for Chromecast devices...")
        chromecasts, browser = pychromecast.get_chromecasts()
        print(f"Found {len(chromecasts)} Chromecast devices.")

        for chromecast in chromecasts:
            print(f"Chromecast found: {chromecast.device.friendly_name}")
            if chromecast.status.is_active_input:
                print(f"{chromecast.device.friendly_name} is active and casting.")
            else:
                print(f"{chromecast.device.friendly_name} is idle.")
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    detect_chromecast()
