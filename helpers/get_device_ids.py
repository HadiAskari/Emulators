from ppadb.client import Client as AdbClient


adb_client = AdbClient(host="127.0.0.1", port=5037)

def get_connected_devices():
    for id, device in enumerate(adb_client.devices()):
        print(id, device.serial)


if __name__ == '__main__':
    get_connected_devices()