from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException

class NFCReader:
    """
    NFC reader wrapper for ACS ACR122U using pyscard.
    Non-blocking: fast-fail connect() if no card, no protocol errors logged.
    """

    def __init__(self):
        self.reader = None

        available_readers = readers()
        if not available_readers:
            print("⚠ No NFC reader found")
        else:
            self.reader = available_readers[0]
            print(f"✅ NFC reader detected: {self.reader}")

    def get_name(self):
        return str(self.reader) if self.reader else None

    def read_uid(self):
        if self.reader is None:
            return None

        connection = None
        try:
            connection = self.reader.createConnection()
            connection.connect()  # Fast fail if no card or unresponsive

            # GET UID APDU
            uid_apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(uid_apdu)

            if sw1 == 0x90 and sw2 == 0x00 and data:
                uid = ''.join(['%02X' % b for b in data])
                return uid
            else:
                return None

        except (NoCardException, CardConnectionException):
            # No card present - normal, silent
            pass
        except Exception as e:
            print(f"⚠ NFC error: {e}")
        finally:
            if connection:
                try:
                    connection.disconnect()
                except:
                    pass

        return None

    def close(self):
        self.reader = None

