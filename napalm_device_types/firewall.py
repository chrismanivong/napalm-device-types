"""
Abstract base class for firewall drivers.

Usage::

    from napalm_device_types import FirewallDriver

    class FortiGateDriver(FirewallDriver):
        def get_security_zones(self):
            ...
"""

from typing import Any, Dict, List
from napalm.base import NetworkDriver
from napalm_device_types.models import (
    NATTranslationDict,
    PackageDict,
    SecurityZoneDict,
    SessionDict,
    VPNTunnelDict,
)


class FirewallDriver(NetworkDriver):
    """
    Abstract intermediate driver for firewall/security devices.

    Inherits all standard NAPALM NetworkDriver methods (including
    ``get_firewall_policies()``) and adds firewall-specific operations
    that concrete drivers must implement.
    """

    def get_nat_translations(self) -> List[NATTranslationDict]:
        """
        Returns a list of active NAT translation entries.

        Each entry contains:

        * protocol (string) - ``"tcp"``, ``"udp"``, ``"icmp"``
        * inside_local (string) - original source address (IP or IP:port)
        * inside_global (string) - translated source address (IP or IP:port)
        * outside_local (string) - destination as seen from inside
        * outside_global (string) - actual destination address
        * age (float) - translation entry age in seconds

        Example::

            [
                {
                    "protocol": "tcp",
                    "inside_local": "192.168.1.10:54321",
                    "inside_global": "203.0.113.1:54321",
                    "outside_local": "1.1.1.1:443",
                    "outside_global": "1.1.1.1:443",
                    "age": 120.5,
                }
            ]
        """
        raise NotImplementedError

    def get_security_zones(self) -> Dict[str, SecurityZoneDict]:
        """
        Returns the security zone configuration.

        Keys are zone names.  Each value contains:

        * interfaces (list of strings) - interfaces assigned to this zone
        * policy (string) - name of the security policy applied to this zone
        * description (string) - zone description

        Example::

            {
                "LAN": {
                    "interfaces": ["eth0", "eth1"],
                    "policy": "LAN-policy",
                    "description": "Internal LAN zone",
                },
                "WAN": {
                    "interfaces": ["eth2"],
                    "policy": "WAN-policy",
                    "description": "Uplink to internet",
                },
            }
        """
        raise NotImplementedError

    def get_sessions(self) -> List[SessionDict]:
        """
        Returns a list of active connection sessions (stateful flows).

        Each entry contains:

        * protocol (string) - ``"tcp"``, ``"udp"``, ``"icmp"``
        * src_ip (string) - source IP address
        * src_port (int) - source port (0 for ICMP)
        * dst_ip (string) - destination IP address
        * dst_port (int) - destination port (0 for ICMP)
        * state (string) - session state, e.g. ``"established"``, ``"syn_sent"``
        * age (float) - session age in seconds

        Example::

            [
                {
                    "protocol": "tcp",
                    "src_ip": "192.168.1.10",
                    "src_port": 54321,
                    "dst_ip": "1.1.1.1",
                    "dst_port": 443,
                    "state": "established",
                    "age": 30.2,
                }
            ]
        """
        raise NotImplementedError

    def get_vpn_tunnels(self) -> Dict[str, VPNTunnelDict]:
        """
        Returns the status of VPN tunnels.

        Keys are tunnel names or identifiers.  Each value contains:

        * type (string) - tunnel type: ``"IPsec"``, ``"SSL"``, ``"GRE"``, ``"WireGuard"``
        * local_endpoint (string) - local tunnel endpoint IP
        * remote_endpoint (string) - remote tunnel endpoint IP
        * is_up (bool) - whether the tunnel is operationally up
        * uptime (int) - tunnel uptime in seconds (0 if down)
        * bytes_in (int) - total bytes received through the tunnel
        * bytes_out (int) - total bytes sent through the tunnel

        Example::

            {
                "vpn-to-branch": {
                    "type": "IPsec",
                    "local_endpoint": "203.0.113.1",
                    "remote_endpoint": "198.51.100.1",
                    "is_up": True,
                    "uptime": 86400,
                    "bytes_in": 104857600,
                    "bytes_out": 52428800,
                }
            }
        """
        raise NotImplementedError

    def get_packages(self) -> List[PackageDict]:
        """
        Returns all packages / plugins currently known to the firewall's
        package manager (e.g. ``pkg`` on pfSense/OPNsense, ``FortiGate
        License`` add-ons, ``apt`` on Debian-based firewalls).

        Each entry contains:

        * name (string) - package name
        * version (string) - installed or available version string
        * installed (bool) - ``True`` if the package is currently installed
        * description (string) - short package description
        * size (int) - package size in bytes (0 if unknown)
        * source (string) - repository / channel the package comes from

        Example::

            [
                {
                    "name": "pfBlockerNG",
                    "version": "3.2.0_4",
                    "installed": True,
                    "description": "IP and DNS blocking for pfSense",
                    "size": 2097152,
                    "source": "pfSense-pkg",
                },
                {
                    "name": "suricata",
                    "version": "7.0.3_1",
                    "installed": False,
                    "description": "High-performance Network IDS/IPS",
                    "size": 51380224,
                    "source": "pfSense-pkg",
                },
            ]
        """
        raise NotImplementedError

    def install_package(self, name: str, version: str = "") -> None:
        """
        Installs a package or plugin on the firewall.

        The method blocks until the installation is complete.  Whether a
        reboot is required afterwards depends on the device; check the vendor
        documentation.

        :param name: Package name as known to the package manager.
        :param version: Exact version to install.  An empty string (default)
            installs the latest available version.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package name is unknown or the requested
            version is not available.
        :raises RuntimeError: If the installation fails on the device side
            (e.g. license missing, dependency conflict, disk full).

        Example::

            driver.install_package("pfBlockerNG")
            driver.install_package("suricata", version="7.0.3_1")
        """
        raise NotImplementedError

    def remove_package(self, name: str) -> None:
        """
        Removes an installed package or plugin from the firewall.

        The method blocks until the removal is complete.

        :param name: Package name to remove.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not currently installed.
        :raises RuntimeError: If the removal fails on the device side
            (e.g. the package is a system dependency).

        Example::

            driver.remove_package("pfBlockerNG")
        """
        raise NotImplementedError

    def get_package_config(self, name: str) -> Dict[str, Any]:
        """
        Returns the current configuration of an installed package or plugin
        as a dictionary.  The structure is package-specific.

        :param name: Package name.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not installed.

        Example::

            driver.get_package_config("pfBlockerNG")
            # →
            {
                "enable": True,
                "maxmind_key": "",
                "blocklists": [
                    {"name": "PRI1", "action": "Deny_Both", "enabled": True},
                    {"name": "DNSBL_ADs", "action": "Unbound", "enabled": True},
                ],
                "update_interval": "Once a day",
            }
        """
        raise NotImplementedError

    def set_package_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Writes a new configuration for an installed package or plugin.

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
                "pfBlockerNG",
                {
                    "enable": True,
                    "blocklists": [
                        {"name": "PRI1", "action": "Deny_Both", "enabled": True},
                    ],
                    "update_interval": "Twice a day",
                },
            )
        """
        raise NotImplementedError
