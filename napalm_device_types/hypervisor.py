"""
Abstract base class for hypervisor drivers.

Usage::

    from napalm_device_types import HypervisorDriver

    class ProxmoxDriver(HypervisorDriver):
        def get_vms(self):
            ...
"""

from typing import Any, Dict, List
from napalm.base import NetworkDriver
from napalm_device_types.models import (
    PackageDict,
    SnapshotDict,
    StorageVolumeDict,
    VMConfigDict,
    VMDict,
    VirtualNetworkDict,
)


class HypervisorDriver(NetworkDriver):
    """
    Abstract intermediate driver for hypervisors and virtualisation platforms
    (e.g. Proxmox VE, VMware ESXi, KVM/libvirt, Hyper-V).

    Inherits all standard NAPALM NetworkDriver methods and adds
    hypervisor-specific operations that concrete drivers must implement.
    """

    # ------------------------------------------------------------------
    # Virtual machines – read
    # ------------------------------------------------------------------

    def get_vms(self) -> List[VMDict]:
        """
        Returns a list of all virtual machines known to this hypervisor,
        including their runtime status.

        Each entry contains:

        * name (string) - VM display name
        * vmid (int) - hypervisor-internal numeric ID
        * status (string) - ``"running"``, ``"stopped"``, ``"paused"``, ``"suspended"``
        * vcpus (int) - number of virtual CPUs assigned
        * memory (int) - configured RAM in megabytes
        * cpu_usage (float) - current CPU utilisation 0.0–1.0
        * memory_usage (int) - current RAM usage in megabytes
        * uptime (int) - uptime in seconds (0 if not running)
        * node (string) - cluster node this VM lives on (empty string for standalone)

        Example::

            [
                {
                    "name": "web01",
                    "vmid": 100,
                    "status": "running",
                    "vcpus": 4,
                    "memory": 8192,
                    "cpu_usage": 0.12,
                    "memory_usage": 3200,
                    "uptime": 864000,
                    "node": "pve1",
                },
                {
                    "name": "db-backup",
                    "vmid": 101,
                    "status": "stopped",
                    "vcpus": 2,
                    "memory": 4096,
                    "cpu_usage": 0.0,
                    "memory_usage": 0,
                    "uptime": 0,
                    "node": "pve1",
                },
            ]
        """
        raise NotImplementedError

    def get_vm_config(self, name: str) -> VMConfigDict:
        """
        Returns the full hardware configuration of a virtual machine.

        :param name: VM name or numeric VMID as a string.
        :raises ValueError: If no VM with the given name/ID exists.

        The returned dictionary contains:

        * name (string) - VM display name
        * vmid (int) - hypervisor-internal numeric ID
        * vcpus (int) - number of virtual CPUs
        * memory (int) - RAM in megabytes
        * os_type (string) - guest OS type hint (e.g. ``"l26"``, ``"win11"``, ``"other"``)
        * boot_order (list of strings) - boot device sequence (e.g. ``["scsi0", "net0"]``)
        * disks (list) - attached virtual disks, each with:

          * device (string) - device ID (e.g. ``"scsi0"``)
          * storage (string) - backing storage pool
          * size (int) - disk size in gigabytes
          * format (string) - image format: ``"qcow2"``, ``"raw"``, ``"vmdk"``
          * bootable (bool) - whether this disk is in the boot order

        * nics (list) - virtual network interfaces, each with:

          * device (string) - device ID (e.g. ``"net0"``)
          * mac (string) - MAC address
          * model (string) - NIC model (e.g. ``"virtio"``, ``"e1000"``)
          * bridge (string) - host bridge the NIC is connected to
          * vlan_id (int) - VLAN tag (0 = untagged)

        * description (string) - free-text notes / description
        * tags (list of strings) - organisational tags

        Example::

            {
                "name": "web01",
                "vmid": 100,
                "vcpus": 4,
                "memory": 8192,
                "os_type": "l26",
                "boot_order": ["scsi0"],
                "disks": [
                    {
                        "device": "scsi0",
                        "storage": "local-lvm",
                        "size": 32,
                        "format": "raw",
                        "bootable": True,
                    }
                ],
                "nics": [
                    {
                        "device": "net0",
                        "mac": "BC:24:11:AA:BB:CC",
                        "model": "virtio",
                        "bridge": "vmbr0",
                        "vlan_id": 10,
                    }
                ],
                "description": "Production web server",
                "tags": ["prod", "web"],
            }
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Virtual machines – power actions
    # ------------------------------------------------------------------

    def start_vm(self, name: str) -> None:
        """
        Powers on a stopped or suspended virtual machine.

        The method blocks until the hypervisor reports the VM as running.

        :param name: VM name or numeric VMID as a string.
        :raises ValueError: If no VM with the given name/ID exists.
        :raises RuntimeError: If the VM cannot be started (e.g. resource limit).

        Example::

            driver.start_vm("web01")
        """
        raise NotImplementedError

    def stop_vm(self, name: str, force: bool = False) -> None:
        """
        Shuts down a virtual machine.

        With ``force=False`` (default) a graceful ACPI shutdown is requested
        and the method blocks until the VM is stopped.  With ``force=True``
        the VM is immediately powered off (equivalent to pulling the plug).

        :param name: VM name or numeric VMID as a string.
        :param force: ``True`` for immediate power-off, ``False`` for graceful shutdown.
        :raises ValueError: If no VM with the given name/ID exists.
        :raises RuntimeError: If the VM is already stopped.

        Example::

            driver.stop_vm("web01")           # graceful
            driver.stop_vm("web01", force=True)  # hard off
        """
        raise NotImplementedError

    def reboot_vm(self, name: str, force: bool = False) -> None:
        """
        Reboots a virtual machine.

        With ``force=False`` (default) a graceful ACPI reboot is requested.
        With ``force=True`` the VM is reset immediately without OS shutdown.

        :param name: VM name or numeric VMID as a string.
        :param force: ``True`` for an immediate reset, ``False`` for graceful reboot.
        :raises ValueError: If no VM with the given name/ID exists.
        :raises RuntimeError: If the VM is not currently running.

        Example::

            driver.reboot_vm("web01")
            driver.reboot_vm("web01", force=True)
        """
        raise NotImplementedError

    def suspend_vm(self, name: str) -> None:
        """
        Suspends (pauses) a running virtual machine, preserving its in-memory
        state.  The VM can be resumed with :meth:`start_vm`.

        :param name: VM name or numeric VMID as a string.
        :raises ValueError: If no VM with the given name/ID exists.
        :raises RuntimeError: If the VM is not currently running.

        Example::

            driver.suspend_vm("web01")
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    def get_snapshots(self, name: str) -> List[SnapshotDict]:
        """
        Returns all snapshots of a virtual machine.

        :param name: VM name or numeric VMID as a string.
        :raises ValueError: If no VM with the given name/ID exists.

        Each entry contains:

        * name (string) - snapshot name
        * vm (string) - VM name this snapshot belongs to
        * created (float) - creation timestamp (Unix epoch)
        * description (string) - optional snapshot description
        * has_memory (bool) - whether the snapshot includes RAM state
        * parent (string) - name of the parent snapshot (empty string for root)

        Example::

            [
                {
                    "name": "before-upgrade",
                    "vm": "web01",
                    "created": 1746921600.0,
                    "description": "Clean state before kernel upgrade",
                    "has_memory": False,
                    "parent": "",
                },
                {
                    "name": "post-upgrade",
                    "vm": "web01",
                    "created": 1746925200.0,
                    "description": "",
                    "has_memory": False,
                    "parent": "before-upgrade",
                },
            ]
        """
        raise NotImplementedError

    def snapshot_create(self, name: str, snapshot: str,
                        description: str = "", include_memory: bool = False) -> None:
        """
        Creates a snapshot of a virtual machine.

        :param name: VM name or numeric VMID as a string.
        :param snapshot: Name for the new snapshot.
        :param description: Optional human-readable description.
        :param include_memory: Whether to include the current RAM state
            (only possible while the VM is running).
        :raises ValueError: If no VM with the given name/ID exists, or a
            snapshot with that name already exists.
        :raises RuntimeError: If snapshot creation fails.

        Example::

            driver.snapshot_create("web01", "before-upgrade",
                                   description="Clean state before kernel upgrade")
        """
        raise NotImplementedError

    def snapshot_delete(self, name: str, snapshot: str) -> None:
        """
        Deletes a snapshot of a virtual machine.

        :param name: VM name or numeric VMID as a string.
        :param snapshot: Name of the snapshot to delete.
        :raises ValueError: If the VM or snapshot does not exist.
        :raises RuntimeError: If other snapshots depend on this one (must delete children first).

        Example::

            driver.snapshot_delete("web01", "before-upgrade")
        """
        raise NotImplementedError

    def snapshot_rollback(self, name: str, snapshot: str) -> None:
        """
        Reverts a virtual machine to a previously created snapshot.

        The VM is stopped (if running), reverted, and then left in the state
        the snapshot recorded (running or stopped depending on ``has_memory``).

        :param name: VM name or numeric VMID as a string.
        :param snapshot: Name of the snapshot to roll back to.
        :raises ValueError: If the VM or snapshot does not exist.
        :raises RuntimeError: If the rollback fails.

        Example::

            driver.snapshot_rollback("web01", "before-upgrade")
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    def get_storage(self) -> Dict[str, StorageVolumeDict]:
        """
        Returns the storage pools / datastores configured on this hypervisor.

        Keys are storage pool names.  Each value contains:

        * name (string) - pool name (repeated for convenience)
        * type (string) - backend type: ``"dir"``, ``"lvm"``, ``"zfs"``,
          ``"nfs"``, ``"ceph"``, ``"iscsi"`` etc.
        * total (int) - total capacity in bytes
        * used (int) - used space in bytes
        * available (int) - free space in bytes
        * enabled (bool) - whether the pool is administratively enabled
        * shared (bool) - whether the pool is accessible from multiple cluster nodes

        Example::

            {
                "local-lvm": {
                    "name": "local-lvm",
                    "type": "lvm",
                    "total": 107374182400,
                    "used": 53687091200,
                    "available": 53687091200,
                    "enabled": True,
                    "shared": False,
                },
                "ceph-pool": {
                    "name": "ceph-pool",
                    "type": "ceph",
                    "total": 1099511627776,
                    "used": 274877906944,
                    "available": 824633720832,
                    "enabled": True,
                    "shared": True,
                },
            }
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Virtual networking
    # ------------------------------------------------------------------

    def get_virtual_networks(self) -> Dict[str, VirtualNetworkDict]:
        """
        Returns the virtual networks / bridges defined on this hypervisor.

        Keys are network names.  Each value contains:

        * name (string) - network name (repeated for convenience)
        * type (string) - network type: ``"bridge"``, ``"ovs"``, ``"nat"``, ``"vxlan"``
        * bridge (string) - underlying host bridge interface
        * vlan_id (int) - associated VLAN tag (0 = untagged / all VLANs)
        * autostart (bool) - whether the network starts automatically at boot
        * active (bool) - whether the network is currently active

        Example::

            {
                "vmbr0": {
                    "name": "vmbr0",
                    "type": "bridge",
                    "bridge": "vmbr0",
                    "vlan_id": 0,
                    "autostart": True,
                    "active": True,
                },
                "vmbr10": {
                    "name": "vmbr10",
                    "type": "bridge",
                    "bridge": "vmbr10",
                    "vlan_id": 10,
                    "autostart": True,
                    "active": True,
                },
            }
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Package management (hypervisor extensions / plugins)
    # ------------------------------------------------------------------

    def get_packages(self) -> List[PackageDict]:
        """
        Returns all packages known to the hypervisor's package manager
        (e.g. ``apt`` on Proxmox VE, vendor extension bundles on ESXi).

        Each entry contains:

        * name (string) - package name
        * version (string) - installed or available version string
        * installed (bool) - ``True`` if the package is currently installed
        * description (string) - short package description
        * size (int) - package size in bytes (0 if unknown)
        * source (string) - repository the package comes from

        Example::

            [
                {
                    "name": "proxmox-backup-client",
                    "version": "3.2.4-1",
                    "installed": True,
                    "description": "Proxmox Backup Client tools",
                    "size": 8388608,
                    "source": "pve-no-subscription",
                },
                {
                    "name": "ifupdown2",
                    "version": "3.2.0-1+pmx4",
                    "installed": True,
                    "description": "Network interface management daemon",
                    "size": 524288,
                    "source": "pve-no-subscription",
                },
            ]
        """
        raise NotImplementedError

    def install_package(self, name: str, version: str = "") -> None:
        """
        Installs a package on the hypervisor host.

        :param name: Package name as known to the package manager.
        :param version: Exact version to install.  Empty string installs latest.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package name is unknown or the version unavailable.
        :raises RuntimeError: If the installation fails on the host side.

        Example::

            driver.install_package("proxmox-backup-client")
        """
        raise NotImplementedError

    def remove_package(self, name: str) -> None:
        """
        Removes an installed package from the hypervisor host.

        :param name: Package name to remove.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not currently installed.
        :raises RuntimeError: If removal fails (e.g. required dependency).

        Example::

            driver.remove_package("proxmox-backup-client")
        """
        raise NotImplementedError

    def get_package_config(self, name: str) -> Dict[str, Any]:
        """
        Returns the current configuration of an installed hypervisor package
        as a dictionary.  The structure is package-specific.

        :param name: Package name.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not installed.

        Example::

            driver.get_package_config("proxmox-backup-client")
            # →
            {
                "server": "backup.corp.example",
                "datastore": "vm-backups",
                "fingerprint": "AB:CD:EF:...",
                "schedule": "daily",
                "retention": {"keep_last": 7, "keep_weekly": 4},
            }
        """
        raise NotImplementedError

    def set_package_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Writes a new configuration for an installed hypervisor package.

        :param name: Package name.
        :param config: New configuration as a nested dictionary.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not installed or config is invalid.
        :raises RuntimeError: If the device rejects the configuration.

        Example::

            driver.set_package_config(
                "proxmox-backup-client",
                {
                    "server": "backup.corp.example",
                    "datastore": "vm-backups",
                    "schedule": "daily",
                    "retention": {"keep_last": 14, "keep_weekly": 4},
                },
            )
        """
        raise NotImplementedError
