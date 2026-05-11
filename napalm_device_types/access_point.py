"""
Abstract base class for wireless access point drivers.

Usage::

    from napalm_device_types import AccessPointDriver

    class OpenWrtDriver(AccessPointDriver):
        def get_wireless_clients(self):
            ...
"""

from typing import Any, Dict, List
from napalm.base import NetworkDriver
from napalm_device_types.models import (
    Dot1XConfigDict,
    FastTransitionConfigDict,
    MACACLDict,
    MeshConfigDict,
    MeshPeerDict,
    PackageDict,
    RadioStatusDict,
    SSIDBridgeDict,
    SSIDDict,
    WirelessClientDict,
    WirelessConfigDict,
)


class AccessPointDriver(NetworkDriver):
    """
    Abstract intermediate driver for wireless access points.

    Inherits all standard NAPALM NetworkDriver methods and adds
    access-point-specific operations that concrete drivers must implement.
    """

    def get_wireless_clients(self) -> List[WirelessClientDict]:
        """
        Returns a list of wireless clients currently associated with this
        access point.

        Each entry contains:

        * mac (string) - client MAC address
        * ssid (string) - SSID the client is connected to
        * radio (string) - radio identifier (e.g. ``"radio0"``, ``"5GHz"``)
        * signal (int) - received signal strength in dBm
        * noise (int) - noise floor in dBm
        * tx_rate (float) - TX bitrate in Mbit/s
        * rx_rate (float) - RX bitrate in Mbit/s
        * uptime (int) - association duration in seconds

        Example::

            [
                {
                    "mac": "AA:BB:CC:DD:EE:FF",
                    "ssid": "MyNetwork",
                    "radio": "radio1",
                    "signal": -65,
                    "noise": -95,
                    "tx_rate": 300.0,
                    "rx_rate": 144.0,
                    "uptime": 3600,
                }
            ]
        """
        raise NotImplementedError

    def get_ssids(self) -> Dict[str, SSIDDict]:
        """
        Returns the configured SSIDs (VAPs) on this access point.

        Keys are SSID names.  Each value contains:

        * enabled (bool) - whether the SSID is currently broadcasting
        * radio (string) - radio the SSID is bound to
        * bssid (string) - BSSID (MAC) of the VAP
        * encryption (string) - e.g. ``"WPA2-PSK"``, ``"WPA3-SAE"``, ``"open"``
        * hidden (bool) - whether the SSID is hidden
        * clients (int) - number of currently associated clients

        Example::

            {
                "MyNetwork": {
                    "enabled": True,
                    "radio": "radio1",
                    "bssid": "AA:BB:CC:DD:EE:F0",
                    "encryption": "WPA2-PSK",
                    "hidden": False,
                    "clients": 3,
                },
                "GuestNet": {
                    "enabled": True,
                    "radio": "radio0",
                    "bssid": "AA:BB:CC:DD:EE:F1",
                    "encryption": "WPA2-PSK",
                    "hidden": False,
                    "clients": 1,
                },
            }
        """
        raise NotImplementedError

    def get_radio_status(self) -> Dict[str, RadioStatusDict]:
        """
        Returns the status of each radio interface.

        Keys are radio identifiers (e.g. ``"radio0"``, ``"radio1"``).
        Each value contains:

        * enabled (bool) - whether the radio is active
        * band (string) - frequency band, e.g. ``"2.4GHz"``, ``"5GHz"``, ``"6GHz"``
        * channel (int) - operating channel number
        * channel_width (int) - channel width in MHz (e.g. 20, 40, 80, 160)
        * tx_power (int) - transmit power in dBm
        * frequency (float) - center frequency in MHz

        Example::

            {
                "radio0": {
                    "enabled": True,
                    "band": "2.4GHz",
                    "channel": 6,
                    "channel_width": 20,
                    "tx_power": 20,
                    "frequency": 2437.0,
                },
                "radio1": {
                    "enabled": True,
                    "band": "5GHz",
                    "channel": 36,
                    "channel_width": 80,
                    "tx_power": 23,
                    "frequency": 5180.0,
                },
            }
        """
        raise NotImplementedError

    def get_wireless_config(self) -> WirelessConfigDict:
        """
        Returns global wireless configuration parameters that apply across
        all radios and SSIDs.

        * country_code (string) - ISO 3166-1 alpha-2 country code (e.g. ``"DE"``)
        * regulatory_domain (string) - regulatory domain string (e.g. ``"ETSI"``)
        * beacon_interval (int) - beacon interval in TUs (default 100)
        * dtim_period (int) - DTIM period (default 2)
        * rts_threshold (int) - RTS/CTS threshold in bytes (2347 = disabled)
        * fragmentation_threshold (int) - fragmentation threshold in bytes
        * short_preamble (bool) - whether short preamble is enabled
        * wmm_enabled (bool) - whether WMM/QoS is enabled

        Example::

            {
                "country_code": "DE",
                "regulatory_domain": "ETSI",
                "beacon_interval": 100,
                "dtim_period": 2,
                "rts_threshold": 2347,
                "fragmentation_threshold": 2346,
                "short_preamble": True,
                "wmm_enabled": True,
            }
        """
        raise NotImplementedError

    def get_fast_transition_config(self) -> Dict[str, FastTransitionConfigDict]:
        """
        Returns the 802.11r Fast BSS Transition (FT) configuration per SSID.

        Keys are SSID names.  Each value contains:

        * enabled (bool) - whether FT is active on this SSID
        * ssid (string) - SSID name (repeated for convenience)
        * mobility_domain (string) - 4-hex-digit Mobility Domain ID (MDID)
        * reassociation_deadline (int) - FT reassociation deadline in TUs
        * r0_key_lifetime (int) - PMK-R0 key lifetime in minutes
        * r1_key_holder (string) - R1 Key Holder identifier (MAC-like string)
        * pmk_r1_push (bool) - whether PMK-R1 is proactively pushed to neighbours
        * over_ds (bool) - whether FT over DS (instead of FT over air) is used

        Example::

            {
                "CorpWiFi": {
                    "enabled": True,
                    "ssid": "CorpWiFi",
                    "mobility_domain": "a1b2",
                    "reassociation_deadline": 1000,
                    "r0_key_lifetime": 10000,
                    "r1_key_holder": "00:11:22:33:44:55",
                    "pmk_r1_push": True,
                    "over_ds": False,
                }
            }
        """
        raise NotImplementedError

    def get_mesh_config(self) -> Dict[str, MeshConfigDict]:
        """
        Returns the 802.11s mesh configuration per mesh interface.

        Keys are mesh interface names (e.g. ``"mesh0"``).  Each value contains:

        * enabled (bool) - whether the mesh interface is active
        * radio (string) - underlying radio (e.g. ``"radio0"``)
        * mesh_id (string) - 802.11s Mesh ID (analogous to SSID)
        * path_metric (string) - path selection metric, e.g. ``"airtime"`` or ``"hopcount"``
        * gate_announcements (bool) - whether gate announcements (GANN) are sent
        * is_gate (bool) - whether this node acts as a mesh gate to the DS
        * encryption (string) - e.g. ``"SAE"``, ``"open"``

        Example::

            {
                "mesh0": {
                    "enabled": True,
                    "radio": "radio1",
                    "mesh_id": "office-mesh",
                    "path_metric": "airtime",
                    "gate_announcements": True,
                    "is_gate": True,
                    "encryption": "SAE",
                }
            }
        """
        raise NotImplementedError

    def get_mesh_peers(self) -> List[MeshPeerDict]:
        """
        Returns a list of currently active 802.11s mesh peers.

        Each entry contains:

        * mac (string) - peer MAC address
        * radio (string) - radio on which the peering was established
        * signal (int) - received signal strength in dBm
        * tx_rate (float) - TX bitrate to peer in Mbit/s
        * rx_rate (float) - RX bitrate from peer in Mbit/s
        * uptime (int) - peering duration in seconds
        * hop_count (int) - number of hops to the mesh gate (0 = this node is the gate)

        Example::

            [
                {
                    "mac": "AA:BB:CC:DD:EE:01",
                    "radio": "radio1",
                    "signal": -58,
                    "tx_rate": 300.0,
                    "rx_rate": 270.0,
                    "uptime": 7200,
                    "hop_count": 1,
                }
            ]
        """
        raise NotImplementedError

    def get_ssid_bridge_config(self) -> Dict[str, SSIDBridgeDict]:
        """
        Returns the Layer-2 bridging configuration for each SSID, i.e. which
        bridge interface and VLAN each SSID is mapped to.

        Keys are SSID names.  Each value contains:

        * ssid (string) - SSID name (repeated for convenience)
        * bridge (string) - bridge interface the VAP is attached to (e.g. ``"br-lan"``, ``"br-guest"``)
        * vlan_id (int) - 802.1Q VLAN ID (0 = untagged / no VLAN separation)
        * tagged (bool) - whether traffic is 802.1Q-tagged on the uplink port
        * client_isolation (bool) - whether clients on this SSID are isolated from each other

        Example::

            {
                "CorpWiFi": {
                    "ssid": "CorpWiFi",
                    "bridge": "br-corp",
                    "vlan_id": 10,
                    "tagged": True,
                    "client_isolation": False,
                },
                "GuestNet": {
                    "ssid": "GuestNet",
                    "bridge": "br-guest",
                    "vlan_id": 20,
                    "tagged": True,
                    "client_isolation": True,
                },
                "IoT": {
                    "ssid": "IoT",
                    "bridge": "br-iot",
                    "vlan_id": 30,
                    "tagged": True,
                    "client_isolation": True,
                },
            }
        """
        raise NotImplementedError

    def get_mac_acl(self) -> Dict[str, MACACLDict]:
        """
        Returns the MAC-address-based access control lists configured per SSID.

        Keys are SSID names.  Each value contains:

        * ssid (string) - SSID name (repeated for convenience)
        * policy (string) - ACL mode:

          * ``"allow"`` – whitelist: only listed MACs may associate
          * ``"deny"``  – blacklist: listed MACs are blocked
          * ``"disabled"`` – no MAC filtering active

        * entries (list) - ACL entries, each with:

          * mac (string) - MAC address (normalised, colon-separated)
          * action (string) - ``"allow"`` or ``"deny"``
          * description (string) - optional human-readable label

        Example::

            {
                "CorpWiFi": {
                    "name": "CorpWiFi",
                    "policy": "allow",
                    "entries": [
                        {"mac": "AA:BB:CC:DD:EE:01", "action": "allow", "description": "CEO-Laptop"},
                        {"mac": "AA:BB:CC:DD:EE:02", "action": "allow", "description": "CFO-Laptop"},
                    ],
                },
                "GuestNet": {
                    "name": "GuestNet",
                    "policy": "deny",
                    "entries": [
                        {"mac": "DE:AD:BE:EF:00:01", "action": "deny", "description": "blocked device"},
                    ],
                },
            }
        """
        raise NotImplementedError

    def get_dot1x_config(self) -> Dict[str, Dot1XConfigDict]:
        """
        Returns the 802.1X / WPA-Enterprise (RADIUS) configuration per SSID.

        Keys are SSID names.  Each value contains:

        * enabled (bool) - whether 802.1X authentication is active on this SSID
        * ssid (string) - SSID name (repeated for convenience)
        * auth_server (dict) - RADIUS authentication server:

          * host (string) - IP or FQDN of the RADIUS server
          * port (int) - UDP port (default 1812)
          * timeout (int) - request timeout in seconds
          * retries (int) - number of retransmissions

        * acct_server (dict or None) - RADIUS accounting server (same keys as auth_server,
          ``None`` if accounting is not configured)
        * reauth_interval (int) - re-authentication interval in seconds (0 = disabled)
        * pmksa_caching (bool) - whether PMKSA caching (opportunistic key caching) is enabled

        Note: The RADIUS shared secret is intentionally omitted from the return
        value for security reasons.

        Example::

            {
                "CorpWiFi": {
                    "enabled": True,
                    "ssid": "CorpWiFi",
                    "auth_server": {
                        "host": "radius.corp.example",
                        "port": 1812,
                        "timeout": 5,
                        "retries": 3,
                    },
                    "acct_server": {
                        "host": "radius.corp.example",
                        "port": 1813,
                        "timeout": 5,
                        "retries": 3,
                    },
                    "reauth_interval": 3600,
                    "pmksa_caching": True,
                }
            }
        """
        raise NotImplementedError

    def get_packages(self) -> List[PackageDict]:
        """
        Returns all packages currently known to the device's package manager
        (e.g. ``opkg`` on OpenWrt, ``apk`` on Alpine-based APs).

        Each entry contains:

        * name (string) - package name
        * version (string) - installed or available version string
        * installed (bool) - ``True`` if the package is currently installed
        * description (string) - short package description
        * size (int) - package size in bytes (0 if unknown)
        * source (string) - repository / feed the package comes from

        Example::

            [
                {
                    "name": "luci-app-statistics",
                    "version": "git-24.001.00000-1",
                    "installed": True,
                    "description": "LuCI Statistics application",
                    "size": 20480,
                    "source": "openwrt/packages",
                },
                {
                    "name": "collectd-mod-wireless",
                    "version": "5.12.0-24",
                    "installed": False,
                    "description": "Wireless statistics plugin for collectd",
                    "size": 8192,
                    "source": "openwrt/packages",
                },
            ]
        """
        raise NotImplementedError

    def install_package(self, name: str, version: str = "") -> None:
        """
        Installs a package on the device.

        The method blocks until the installation is complete.  After it returns
        successfully the package is available for use without a reboot
        (where the underlying package manager supports this).

        :param name: Package name as known to the package manager.
        :param version: Exact version to install.  An empty string (default)
            installs the latest available version.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package name is unknown or the version does
            not exist in any configured feed.
        :raises RuntimeError: If the installation fails on the device side
            (e.g. dependency conflict, disk full).

        Example::

            driver.install_package("luci-app-statistics")
            driver.install_package("collectd", version="5.12.0-24")
        """
        raise NotImplementedError

    def remove_package(self, name: str) -> None:
        """
        Removes an installed package from the device.

        The method blocks until the removal is complete.

        :param name: Package name to remove.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not currently installed.
        :raises RuntimeError: If the removal fails on the device side
            (e.g. other packages depend on it).

        Example::

            driver.remove_package("luci-app-statistics")
        """
        raise NotImplementedError

    def get_package_config(self, name: str) -> Dict[str, Any]:
        """
        Returns the current configuration of an installed package as a
        dictionary.  The structure is package-specific.

        :param name: Package name.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not installed.

        Example::

            driver.get_package_config("luci-app-statistics")
            # →
            {
                "collectd": {
                    "enabled": True,
                    "interval": 30,
                },
                "rrdtool": {
                    "datadir": "/tmp/rrd",
                    "stepsize": 30,
                    "heartbeat": 60,
                },
            }
        """
        raise NotImplementedError

    def set_package_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Writes a new configuration for an installed package.

        The ``config`` dict must match the structure returned by
        :meth:`get_package_config`.  Unknown keys are ignored or raise a
        ``ValueError`` depending on the driver implementation.

        Changes take effect immediately where the package supports live
        reload; otherwise a package restart or device reboot may be
        required – behaviour is driver-specific.

        :param name: Package name.
        :param config: New configuration as a nested dictionary.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not installed or the configuration
            contains invalid values.
        :raises RuntimeError: If the device rejects the configuration.

        Example::

            driver.set_package_config(
                "luci-app-statistics",
                {
                    "collectd": {"enabled": True, "interval": 60},
                    "rrdtool": {"datadir": "/tmp/rrd", "stepsize": 60, "heartbeat": 120},
                },
            )
        """
        raise NotImplementedError
