import queue
import threading
from contextlib import suppress
from typing import Any

try:
    import dbus
    import dbus.mainloop.glib
    import dbus.service
    from gi.repository import GLib
except ImportError as exc:
    dbus = None
    GLib = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

NUS_SVC_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

BLUEZ_SERVICE = "org.bluez"
DBUS_PROPERTIES = "org.freedesktop.DBus.Properties"
DBUS_OBJECT_MANAGER = "org.freedesktop.DBus.ObjectManager"
ADAPTER_INTERFACE = "org.bluez.Adapter1"
GATT_MANAGER = "org.bluez.GattManager1"
ADVERTISEMENT_MANAGER = "org.bluez.LEAdvertisingManager1"
SERVICE_INTERFACE = "org.bluez.GattService1"
CHAR_INTERFACE = "org.bluez.GattCharacteristic1"
ADVERTISEMENT_INTERFACE = "org.bluez.LEAdvertisement1"
ADAPTER_PATH = "/org/bluez/hci0"

APP_PATH = "/com/sensors/app"
SERVICE_PATH = f"{APP_PATH}/service0"
RX_PATH = f"{SERVICE_PATH}/char0"
TX_PATH = f"{SERVICE_PATH}/char1"
ADV_PATH = "/com/sensors/adv0"


if dbus is None:
    class BleService:
        def __init__(self, name: str = "HannahRPi") -> None:
            self.name = name
            self._q: queue.Queue[str] = queue.Queue()
            self._error = ""

        def start(self) -> bool:
            self._error = f"missing BLE dependencies: {_IMPORT_ERROR}"
            print(f"[BLE] {self._error}")
            return False

        def stop(self) -> None:
            return None

        def get_message(self) -> str | None:
            try:
                return self._q.get_nowait()
            except queue.Empty:
                return None

else:
    class _InvalidArgs(dbus.exceptions.DBusException):
        _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


    class _RXCharacteristic(dbus.service.Object):
        def __init__(self, bus: Any, message_queue: queue.Queue[str]) -> None:
            super().__init__(bus, RX_PATH)
            self._messages = message_queue

        def get_path(self) -> dbus.ObjectPath:
            return dbus.ObjectPath(RX_PATH)

        def get_properties(self) -> dict[str, dict[str, Any]]:
            return {
                CHAR_INTERFACE: {
                    "UUID": dbus.String(NUS_RX_UUID),
                    "Service": dbus.ObjectPath(SERVICE_PATH),
                    "Flags": dbus.Array(["write", "write-without-response"], signature="s"),
                }
            }

        @dbus.service.method(DBUS_PROPERTIES, in_signature="s", out_signature="a{sv}")
        def GetAll(self, interface: str) -> dict[str, Any]:
            if interface != CHAR_INTERFACE:
                raise _InvalidArgs()
            return self.get_properties()[CHAR_INTERFACE]

        @dbus.service.method(CHAR_INTERFACE, in_signature="aya{sv}", out_signature="")
        def WriteValue(self, value: Any, options: Any) -> None:
            del options
            message = bytes(value).decode("utf-8", errors="replace").strip()
            if message:
                self._messages.put(message)
                print(f"[BLE] RX: {message}")


    class _TXCharacteristic(dbus.service.Object):
        def __init__(self, bus: Any) -> None:
            super().__init__(bus, TX_PATH)
            self._notifying = False
            self._value: list[dbus.Byte] = []

        def get_path(self) -> dbus.ObjectPath:
            return dbus.ObjectPath(TX_PATH)

        def get_properties(self) -> dict[str, dict[str, Any]]:
            return {
                CHAR_INTERFACE: {
                    "UUID": dbus.String(NUS_TX_UUID),
                    "Service": dbus.ObjectPath(SERVICE_PATH),
                    "Flags": dbus.Array(["notify", "read"], signature="s"),
                    "Notifying": dbus.Boolean(self._notifying),
                    "Value": dbus.Array(self._value, signature="y"),
                }
            }

        @dbus.service.method(DBUS_PROPERTIES, in_signature="s", out_signature="a{sv}")
        def GetAll(self, interface: str) -> dict[str, Any]:
            if interface != CHAR_INTERFACE:
                raise _InvalidArgs()
            return self.get_properties()[CHAR_INTERFACE]

        @dbus.service.method(CHAR_INTERFACE, in_signature="a{sv}", out_signature="ay")
        def ReadValue(self, options: Any) -> dbus.Array:
            del options
            return dbus.Array(self._value, signature="y")

        @dbus.service.method(CHAR_INTERFACE, in_signature="", out_signature="")
        def StartNotify(self) -> None:
            self._notifying = True

        @dbus.service.method(CHAR_INTERFACE, in_signature="", out_signature="")
        def StopNotify(self) -> None:
            self._notifying = False


    class _UARTService(dbus.service.Object):
        def __init__(self, bus: Any, message_queue: queue.Queue[str]) -> None:
            super().__init__(bus, SERVICE_PATH)
            self._rx = _RXCharacteristic(bus, message_queue)
            self._tx = _TXCharacteristic(bus)

        @property
        def chars(self) -> tuple[_RXCharacteristic, _TXCharacteristic]:
            return self._rx, self._tx

        def get_path(self) -> dbus.ObjectPath:
            return dbus.ObjectPath(SERVICE_PATH)

        def get_properties(self) -> dict[str, dict[str, Any]]:
            return {
                SERVICE_INTERFACE: {
                    "UUID": dbus.String(NUS_SVC_UUID),
                    "Primary": dbus.Boolean(True),
                    "Characteristics": dbus.Array(
                        [self._rx.get_path(), self._tx.get_path()],
                        signature="o",
                    ),
                }
            }

        @dbus.service.method(DBUS_PROPERTIES, in_signature="s", out_signature="a{sv}")
        def GetAll(self, interface: str) -> dict[str, Any]:
            if interface != SERVICE_INTERFACE:
                raise _InvalidArgs()
            return self.get_properties()[SERVICE_INTERFACE]


    class _Application(dbus.service.Object):
        def __init__(self, bus: Any, message_queue: queue.Queue[str]) -> None:
            super().__init__(bus, APP_PATH)
            self._service = _UARTService(bus, message_queue)

        def get_path(self) -> dbus.ObjectPath:
            return dbus.ObjectPath(APP_PATH)

        @property
        def objects(self) -> tuple[_UARTService, _RXCharacteristic, _TXCharacteristic]:
            rx, tx = self._service.chars
            return self._service, rx, tx

        @dbus.service.method(DBUS_OBJECT_MANAGER, out_signature="a{oa{sa{sv}}}")
        def GetManagedObjects(self) -> dict[dbus.ObjectPath, dict[str, dict[str, Any]]]:
            managed: dict[dbus.ObjectPath, dict[str, dict[str, Any]]] = {}
            for obj in self.objects:
                managed[obj.get_path()] = obj.get_properties()
            return managed


    class _Advertisement(dbus.service.Object):
        def __init__(self, bus: Any, name: str) -> None:
            super().__init__(bus, ADV_PATH)
            self._name = name

        def get_path(self) -> dbus.ObjectPath:
            return dbus.ObjectPath(ADV_PATH)

        def get_properties(self) -> dict[str, dict[str, Any]]:
            return {
                ADVERTISEMENT_INTERFACE: {
                    "Type": dbus.String("peripheral"),
                    "ServiceUUIDs": dbus.Array([NUS_SVC_UUID], signature="s"),
                    "LocalName": dbus.String(self._name),
                    "Includes": dbus.Array(["tx-power"], signature="s"),
                }
            }

        @dbus.service.method(DBUS_PROPERTIES, in_signature="s", out_signature="a{sv}")
        def GetAll(self, interface: str) -> dict[str, Any]:
            if interface != ADVERTISEMENT_INTERFACE:
                raise _InvalidArgs()
            return self.get_properties()[ADVERTISEMENT_INTERFACE]

        @dbus.service.method(ADVERTISEMENT_INTERFACE, in_signature="", out_signature="")
        def Release(self) -> None:
            return None


    class BleService:
        def __init__(self, name: str = "HannahRPi") -> None:
            self.name = name
            self._q: queue.Queue[str] = queue.Queue()
            self._loop: GLib.MainLoop | None = None
            self._thread: threading.Thread | None = None
            self._ready = threading.Event()
            self._pending_registrations = 0
            self._available = False
            self._error = ""
            self._bus: Any = None
            self._app: _Application | None = None
            self._adv: _Advertisement | None = None

        def start(self) -> bool:
            if self._thread is not None and self._thread.is_alive():
                return self._available

            self._ready.clear()
            self._pending_registrations = 2
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

            if not self._ready.wait(timeout=8):
                self._error = "startup timed out"
                self.stop()
                print(f"[BLE] Error: {self._error}")
                return False

            return self._available

        def _run(self) -> None:
            try:
                dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
                self._bus = dbus.SystemBus()
                self._loop = GLib.MainLoop()
                self._configure_adapter()

                self._app = _Application(self._bus, self._q)
                self._adv = _Advertisement(self._bus, self.name)

                adapter = self._bus.get_object(BLUEZ_SERVICE, ADAPTER_PATH)
                gatt_mgr = dbus.Interface(adapter, GATT_MANAGER)
                adv_mgr = dbus.Interface(adapter, ADVERTISEMENT_MANAGER)

                gatt_mgr.RegisterApplication(
                    self._app.get_path(),
                    {},
                    reply_handler=self._registration_ok,
                    error_handler=self._registration_failed,
                )
                adv_mgr.RegisterAdvertisement(
                    self._adv.get_path(),
                    {},
                    reply_handler=self._registration_ok,
                    error_handler=self._registration_failed,
                )
                self._loop.run()
            except Exception as exc:
                self._error = str(exc)
                self._available = False
                self._ready.set()
                print(f"[BLE] Error: {exc}")

        def _configure_adapter(self) -> None:
            adapter = self._bus.get_object(BLUEZ_SERVICE, ADAPTER_PATH)
            props = dbus.Interface(adapter, DBUS_PROPERTIES)
            props.Set(ADAPTER_INTERFACE, "Powered", dbus.Boolean(True))
            with suppress(Exception):
                props.Set(ADAPTER_INTERFACE, "Alias", dbus.String(self.name))
            with suppress(Exception):
                props.Set(ADAPTER_INTERFACE, "Discoverable", dbus.Boolean(True))
            with suppress(Exception):
                props.Set(ADAPTER_INTERFACE, "DiscoverableTimeout", dbus.UInt32(0))
            with suppress(Exception):
                props.Set(ADAPTER_INTERFACE, "Pairable", dbus.Boolean(True))
            with suppress(Exception):
                props.Set(ADAPTER_INTERFACE, "PairableTimeout", dbus.UInt32(0))

        def _registration_ok(self) -> None:
            self._pending_registrations -= 1
            if self._pending_registrations != 0:
                return

            self._available = True
            self._error = ""
            self._ready.set()
            print(f"[BLE] Advertising as {self.name}")

        def _registration_failed(self, error: Exception) -> None:
            self._error = str(error)
            self._available = False
            self._ready.set()
            print(f"[BLE] Error: {error}")
            if self._loop is not None:
                self._loop.quit()

        def stop(self) -> None:
            if self._bus is not None:
                adapter = self._bus.get_object(BLUEZ_SERVICE, ADAPTER_PATH)
                with suppress(Exception):
                    adv_mgr = dbus.Interface(adapter, ADVERTISEMENT_MANAGER)
                    adv_mgr.UnregisterAdvertisement(dbus.ObjectPath(ADV_PATH))
                with suppress(Exception):
                    gatt_mgr = dbus.Interface(adapter, GATT_MANAGER)
                    gatt_mgr.UnregisterApplication(dbus.ObjectPath(APP_PATH))

            if self._loop is not None:
                self._loop.quit()
            if self._thread is not None:
                self._thread.join(timeout=2)

            self._loop = None
            self._thread = None
            self._available = False
            self._bus = None

        def get_message(self) -> str | None:
            try:
                return self._q.get_nowait()
            except queue.Empty:
                return None
