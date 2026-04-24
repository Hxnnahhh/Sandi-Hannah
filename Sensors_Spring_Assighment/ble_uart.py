import queue
import threading

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

_SVC_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
_RX_UUID  = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
_TX_UUID  = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

_APP  = "/org/bluez/sensors_app"
_SVC  = "/org/bluez/sensors_app/svc"
_CHAR = "/org/bluez/sensors_app/svc/char"
_TX   = "/org/bluez/sensors_app/svc/tx"
_ADV  = "/org/bluez/sensors_app/adv"

_PROP_IFACE    = "org.freedesktop.DBus.Properties"
_ADAPTER_IFACE = "org.bluez.Adapter1"
_ADV_IFACE     = "org.bluez.LEAdvertisement1"
_ADV_MGR_IFACE = "org.bluez.LEAdvertisingManager1"


class _Advertisement(dbus.service.Object):

    def __init__(self, bus, name: str):
        super().__init__(bus, _ADV)
        self._name = name

    @dbus.service.method(_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        return {
            "Type":         dbus.String("peripheral"),
            "ServiceUUIDs": dbus.Array([_SVC_UUID], signature="s"),
            "LocalName":    dbus.String(self._name),
        }

    @dbus.service.method(_ADV_IFACE)
    def Release(self):
        print("[BLE] Advertisement released")


class _RXChar(dbus.service.Object):
    def __init__(self, bus, rx_queue):
        super().__init__(bus, _CHAR)
        self._q = rx_queue

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature="aya{sv}")
    def WriteValue(self, value, options):
        del options
        try:
            self._q.put(bytes(value).decode("utf-8", errors="replace"))
        except Exception as e:
            print(f"[BLE] WriteValue error: {e}")


class _TXChar(dbus.service.Object):

    def __init__(self, bus):
        super().__init__(bus, _TX)
        self._notifying = False

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        del options
        return dbus.Array([], signature="y")

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature="a{sv}")
    def StartNotify(self, options):
        del options
        self._notifying = True

    @dbus.service.method("org.bluez.GattCharacteristic1")
    def StopNotify(self):
        self._notifying = False


class _App(dbus.service.Object):
    def __init__(self, bus, rx_queue):
        super().__init__(bus, _APP)
        self._char = _RXChar(bus, rx_queue)
        self._tx   = _TXChar(bus)

    @dbus.service.method("org.freedesktop.DBus.ObjectManager", out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        return {
            dbus.ObjectPath(_SVC): {
                "org.bluez.GattService1": {
                    "UUID": dbus.String(_SVC_UUID),
                    "Primary": dbus.Boolean(True),
                }
            },
            dbus.ObjectPath(_CHAR): {
                "org.bluez.GattCharacteristic1": {
                    "UUID": dbus.String(_RX_UUID),
                    "Service": dbus.ObjectPath(_SVC),
                    "Flags": dbus.Array(["write", "write-without-response"], signature="s"),
                }
            },
            dbus.ObjectPath(_TX): {
                "org.bluez.GattCharacteristic1": {
                    "UUID": dbus.String(_TX_UUID),
                    "Service": dbus.ObjectPath(_SVC),
                    "Flags": dbus.Array(["notify", "read"], signature="s"),
                }
            },
        }


class BLEUARTServer:

    def __init__(self, name: str = "HannahRPi"):
        self._name = name
        self._q = queue.Queue()
        self._loop = None
        self._thread = None
        self._adv = None
        self._app = None
        self._last_message: str | None = None

    def start(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()

        adapter_obj = bus.get_object("org.bluez", "/org/bluez/hci0")

        props = dbus.Interface(adapter_obj, _PROP_IFACE)
        props.Set(_ADAPTER_IFACE, "Alias",        dbus.String(self._name))
        props.Set(_ADAPTER_IFACE, "Powered",       dbus.Boolean(True))
        props.Set(_ADAPTER_IFACE, "Discoverable",  dbus.Boolean(True))

        self._app = _App(bus, self._q)
        self._adv = _Advertisement(bus, self._name)

        self._loop = GLib.MainLoop()
        self._thread = threading.Thread(target=self._loop.run, daemon=True)
        self._thread.start()

        gatt_done = threading.Event()
        adv_done  = threading.Event()

        gatt_mgr = dbus.Interface(adapter_obj, "org.bluez.GattManager1")
        gatt_mgr.RegisterApplication(
            self._app, {},
            reply_handler=lambda:    (print("[BLE] GATT ready"),               gatt_done.set()),
            error_handler=lambda e:  (print(f"[BLE] GATT error: {e}"),         gatt_done.set()),
        )
        gatt_done.wait(timeout=5)

        adv_mgr = dbus.Interface(adapter_obj, _ADV_MGR_IFACE)
        adv_mgr.RegisterAdvertisement(
            dbus.ObjectPath(_ADV), {},
            reply_handler=lambda:    (print(f"[BLE] Advertising as '{self._name}'"), adv_done.set()),
            error_handler=lambda e:  (print(f"[BLE] Adv error: {e}"),               adv_done.set()),
        )
        adv_done.wait(timeout=5)

    def stop(self):
        if self._loop:
            self._loop.quit()
        if self._thread:
            self._thread.join(timeout=2)

    def get_message(self):
        try:
            while True:
                self._last_message = self._q.get_nowait()
        except queue.Empty:
            pass
        return self._last_message
