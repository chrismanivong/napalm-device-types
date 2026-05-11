"""
Abstract base class for storage and NAS/SAN device drivers.

Usage::

    from napalm_device_types import StorageDriver

    class TrueNASDriver(StorageDriver):
        def get_disks(self):
            ...
"""

from typing import Any, Dict, List
from napalm.base import NetworkDriver
from napalm_device_types.models import (
    DiskPoolDict,
    LogicalVolumeDict,
    NASShareDict,
    PackageDict,
    PhysicalDiskDict,
    ReplicationJobDict,
    StorageQuotaDict,
    StorageServiceDict,
    VolumeSnapshotDict,
)


class StorageDriver(NetworkDriver):
    """
    Abstract intermediate driver for storage appliances and NAS/SAN devices
    (e.g. TrueNAS SCALE/CORE, Synology DSM, QNAP QTS, NetApp ONTAP,
    OpenMediaVault, Pure Storage, IBM Storwize).

    Inherits all standard NAPALM NetworkDriver methods and adds
    storage-specific operations that concrete drivers must implement.
    """

    # ------------------------------------------------------------------
    # Physical hardware
    # ------------------------------------------------------------------

    def get_disks(self) -> List[PhysicalDiskDict]:
        """
        Returns all physical drives detected by the storage device.

        Each entry contains:

        * slot (string) - bay or device identifier (e.g. ``"bay1"``, ``"sda"``, ``"nvme0n1"``)
        * model (string) - drive model string
        * serial (string) - drive serial number
        * vendor (string) - drive manufacturer
        * type (string) - ``"hdd"``, ``"ssd"``, or ``"nvme"``
        * size (int) - raw capacity in bytes
        * rpm (int) - rotational speed; ``0`` for SSD/NVMe
        * temperature (int) - current temperature in Celsius; ``-1`` if unavailable
        * health (string) - ``"healthy"``, ``"warning"``, ``"failed"``, or ``"unknown"``
        * pool (string) - name of the pool this disk belongs to; empty string if unassigned/spare

        Example::

            [
                {
                    "slot": "bay1",
                    "model": "HGST HUS726T6TALE6L4",
                    "serial": "K3GXXXXX",
                    "vendor": "HGST",
                    "type": "hdd",
                    "size": 6001175126016,
                    "rpm": 7200,
                    "temperature": 34,
                    "health": "healthy",
                    "pool": "tank",
                },
                {
                    "slot": "bay5",
                    "model": "Samsung SSD 870 EVO 1TB",
                    "serial": "S5XXXXXXX",
                    "vendor": "Samsung",
                    "type": "ssd",
                    "size": 1000204886016,
                    "rpm": 0,
                    "temperature": 28,
                    "health": "healthy",
                    "pool": "fast-pool",
                },
            ]
        """
        raise NotImplementedError

    def get_disk_pools(self) -> Dict[str, DiskPoolDict]:
        """
        Returns the disk pools (RAID arrays, ZFS pools, LVM volume groups, etc.)
        configured on the device.

        Keys are pool names.  Each value contains:

        * name (string) - pool name (repeated for convenience)
        * type (string) - ``"zfs"``, ``"lvm"``, ``"md"``, ``"hardware-raid"``, ``"btrfs"``
        * level (string) - RAID/redundancy level: ``"mirror"``, ``"raidz1"``, ``"raidz2"``,
          ``"raidz3"``, ``"stripe"``, ``"raid0"`` … ``"raid60"``, ``"single"``
        * status (string) - ``"online"``, ``"degraded"``, ``"faulted"``, ``"offline"``, ``"unknown"``
        * total (int) - usable capacity in bytes
        * used (int) - used space in bytes
        * available (int) - free space in bytes
        * disks (list of strings) - slot identifiers of member drives
        * auto_expand (bool) - whether the pool grows automatically when disks are replaced with larger ones
        * dedup (bool) - whether deduplication is enabled
        * compression (string) - pool-level compression algorithm: ``"off"``, ``"lz4"``,
          ``"gzip"``, ``"zstd"``, etc.

        Example::

            {
                "tank": {
                    "name": "tank",
                    "type": "zfs",
                    "level": "raidz2",
                    "status": "online",
                    "total": 21990232555520,
                    "used": 8796093022208,
                    "available": 13194139533312,
                    "disks": ["bay1", "bay2", "bay3", "bay4", "bay5", "bay6"],
                    "auto_expand": True,
                    "dedup": False,
                    "compression": "lz4",
                },
            }
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Logical volumes / datasets
    # ------------------------------------------------------------------

    def get_volumes(self) -> Dict[str, LogicalVolumeDict]:
        """
        Returns all logical volumes, ZFS datasets, or LUNs on the device.

        Keys are volume paths (e.g. ``"tank/data"``, ``"tank/media"``).
        Each value contains:

        * name (string) - volume name (leaf component or full path)
        * pool (string) - parent pool
        * type (string) - ``"filesystem"``, ``"volume"`` (block device / LUN), or ``"zvol"``
        * total (int) - quota or provisioned size in bytes; ``0`` means unlimited
        * used (int) - space currently used in bytes
        * available (int) - space available in bytes
        * mountpoint (string) - local mount path; empty string for block volumes / LUNs
        * compression (string) - active compression algorithm (``"off"``, ``"lz4"``, ``"zstd"``, etc.)
        * dedup (bool) - whether deduplication is active on this volume
        * readonly (bool) - whether the volume is mounted read-only
        * snapshots (int) - number of snapshots currently held

        Example::

            {
                "tank/media": {
                    "name": "media",
                    "pool": "tank",
                    "type": "filesystem",
                    "total": 0,
                    "used": 4398046511104,
                    "available": 13194139533312,
                    "mountpoint": "/mnt/tank/media",
                    "compression": "lz4",
                    "dedup": False,
                    "readonly": False,
                    "snapshots": 7,
                },
                "tank/backups": {
                    "name": "backups",
                    "pool": "tank",
                    "type": "filesystem",
                    "total": 5497558138880,
                    "used": 1099511627776,
                    "available": 4398046511104,
                    "mountpoint": "/mnt/tank/backups",
                    "compression": "zstd",
                    "dedup": False,
                    "readonly": False,
                    "snapshots": 14,
                },
            }
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Shares
    # ------------------------------------------------------------------

    def get_shares(self) -> Dict[str, NASShareDict]:
        """
        Returns all network shares and iSCSI targets exported by the device.

        Keys are share names.  Each value contains:

        * name (string) - share name (repeated for convenience)
        * protocol (string) - ``"nfs"``, ``"smb"``, ``"afp"``, ``"ftp"``, ``"sftp"``,
          ``"iscsi"``, or ``"webdav"``
        * path (string) - local filesystem path; for iSCSI the target IQN
        * volume (string) - logical volume or dataset this share is backed by
        * enabled (bool) - whether the share is currently exported
        * readonly (bool) - whether the share is exported read-only
        * description (string) - optional human-readable description
        * clients (list of strings) - IP address or subnet allow-list;
          empty list means all hosts are permitted

        Example::

            {
                "media": {
                    "name": "media",
                    "protocol": "nfs",
                    "path": "/mnt/tank/media",
                    "volume": "tank/media",
                    "enabled": True,
                    "readonly": False,
                    "description": "Media library",
                    "clients": ["192.168.1.0/24"],
                },
                "homes": {
                    "name": "homes",
                    "protocol": "smb",
                    "path": "/mnt/tank/homes",
                    "volume": "tank/homes",
                    "enabled": True,
                    "readonly": False,
                    "description": "User home directories",
                    "clients": [],
                },
            }
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    def get_volume_snapshots(self, volume: str = "") -> List[VolumeSnapshotDict]:
        """
        Returns volume / dataset snapshots.

        :param volume: Restrict results to this volume path (e.g. ``"tank/media"``).
            Pass an empty string (default) to list snapshots for all volumes.

        Each entry contains:

        * name (string) - snapshot name (e.g. ``"auto-2026-05-11"`` or full ``"tank/media@auto-2026-05-11"``)
        * volume (string) - parent volume / dataset path
        * created (float) - creation timestamp (Unix epoch)
        * size (int) - bytes of unique data referenced only by this snapshot
        * description (string) - optional description
        * clones (list of strings) - volumes that were cloned from this snapshot

        Example::

            [
                {
                    "name": "auto-2026-05-11",
                    "volume": "tank/media",
                    "created": 1746921600.0,
                    "size": 2097152,
                    "description": "Automatic daily snapshot",
                    "clones": [],
                },
                {
                    "name": "before-migration",
                    "volume": "tank/backups",
                    "created": 1746835200.0,
                    "size": 1073741824,
                    "description": "Snapshot before storage migration",
                    "clones": ["tank/backups-clone"],
                },
            ]
        """
        raise NotImplementedError

    def snapshot_create(self, volume: str, name: str, description: str = "") -> None:
        """
        Creates a snapshot of a logical volume or dataset.

        :param volume: Volume / dataset path (e.g. ``"tank/media"``).
        :param name: Name for the new snapshot.
        :param description: Optional human-readable description.
        :raises ValueError: If the volume does not exist, or a snapshot with that
            name already exists.
        :raises RuntimeError: If snapshot creation fails on the device side.

        Example::

            driver.snapshot_create("tank/media", "before-migration",
                                   description="Snapshot before storage migration")
        """
        raise NotImplementedError

    def snapshot_delete(self, volume: str, name: str) -> None:
        """
        Deletes a snapshot of a logical volume or dataset.

        :param volume: Volume / dataset path.
        :param name: Name of the snapshot to delete.
        :raises ValueError: If the volume or snapshot does not exist.
        :raises RuntimeError: If other clones depend on this snapshot
            (delete or promote clones first).

        Example::

            driver.snapshot_delete("tank/media", "auto-2026-05-01")
        """
        raise NotImplementedError

    def snapshot_rollback(self, volume: str, name: str) -> None:
        """
        Reverts a volume / dataset to a previously created snapshot.

        All data written after the snapshot was taken is permanently discarded.
        Any snapshots created after the target snapshot are also deleted.

        :param volume: Volume / dataset path.
        :param name: Name of the snapshot to roll back to.
        :raises ValueError: If the volume or snapshot does not exist.
        :raises RuntimeError: If the rollback fails (e.g. active clones block it).

        Example::

            driver.snapshot_rollback("tank/media", "before-migration")
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Quotas
    # ------------------------------------------------------------------

    def get_quotas(self) -> List[StorageQuotaDict]:
        """
        Returns all filesystem quotas configured on the device.

        Each entry contains:

        * target (string) - username, group name, or dataset path depending on ``target_type``
        * target_type (string) - ``"user"``, ``"group"``, or ``"dataset"``
        * volume (string) - volume / dataset the quota applies to
        * used (int) - bytes currently consumed by this target
        * quota (int) - hard storage limit in bytes; ``0`` means no limit
        * ref_quota (int) - referenced-data limit in bytes (excludes snapshots);
          ``0`` means no limit

        Example::

            [
                {
                    "target": "alice",
                    "target_type": "user",
                    "volume": "tank/homes",
                    "used": 53687091200,
                    "quota": 107374182400,
                    "ref_quota": 0,
                },
                {
                    "target": "tank/backups",
                    "target_type": "dataset",
                    "volume": "tank/backups",
                    "used": 1099511627776,
                    "quota": 5497558138880,
                    "ref_quota": 0,
                },
            ]
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------

    def get_services(self) -> Dict[str, StorageServiceDict]:
        """
        Returns the file-sharing and access services available on the device.

        Keys are service names (e.g. ``"nfs"``, ``"smb"``).  Each value contains:

        * name (string) - service name (repeated for convenience)
        * enabled (bool) - administratively enabled (will start on next boot)
        * running (bool) - currently active and listening
        * port (int) - primary listening port; ``0`` if not applicable
        * version (string) - protocol version string (e.g. ``"4.1"`` for NFSv4.1,
          ``"3.1.1"`` for SMB3); empty string if unknown

        Example::

            {
                "nfs": {
                    "name": "nfs",
                    "enabled": True,
                    "running": True,
                    "port": 2049,
                    "version": "4.2",
                },
                "smb": {
                    "name": "smb",
                    "enabled": True,
                    "running": True,
                    "port": 445,
                    "version": "3.1.1",
                },
                "ftp": {
                    "name": "ftp",
                    "enabled": False,
                    "running": False,
                    "port": 21,
                    "version": "",
                },
            }
        """
        raise NotImplementedError

    def set_service_enabled(self, service: str, enabled: bool) -> None:
        """
        Administratively enables or disables a file-sharing service.

        Disabling stops the service immediately; enabling starts it immediately.

        :param service: Service name (e.g. ``"nfs"``, ``"smb"``, ``"ftp"``).
        :param enabled: ``True`` to start and enable; ``False`` to stop and disable.
        :raises ValueError: If the service name is not recognised.
        :raises RuntimeError: If the operation fails on the device side.

        Example::

            driver.set_service_enabled("ftp", False)  # disable FTP
            driver.set_service_enabled("nfs", True)   # enable NFS
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Replication
    # ------------------------------------------------------------------

    def get_replication_jobs(self) -> List[ReplicationJobDict]:
        """
        Returns all replication / sync jobs configured on the device.

        Each entry contains:

        * name (string) - job name
        * source (string) - source path or dataset
        * target (string) - destination path or dataset; may include a remote
          host prefix (e.g. ``"backup-server:tank/replica"``)
        * direction (string) - ``"push"`` (local → remote) or ``"pull"`` (remote → local)
        * schedule (string) - cron expression or descriptive label (``"daily"``,
          ``"hourly"``, etc.)
        * enabled (bool) - whether the job is scheduled to run
        * last_run (float) - Unix epoch of the last run; ``0.0`` if never run
        * last_status (string) - ``"success"``, ``"failed"``, ``"running"``, or ``"pending"``
        * bytes_sent (int) - bytes transferred in the most recent run; ``0`` if never run

        Example::

            [
                {
                    "name": "media-offsite",
                    "source": "tank/media",
                    "target": "backup-nas:tank/media-replica",
                    "direction": "push",
                    "schedule": "0 2 * * *",
                    "enabled": True,
                    "last_run": 1746921600.0,
                    "last_status": "success",
                    "bytes_sent": 1073741824,
                },
                {
                    "name": "backups-local",
                    "source": "tank/backups",
                    "target": "tank/backups-mirror",
                    "direction": "push",
                    "schedule": "hourly",
                    "enabled": True,
                    "last_run": 1746918000.0,
                    "last_status": "success",
                    "bytes_sent": 104857600,
                },
            ]
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Package management (plugins / extensions)
    # ------------------------------------------------------------------

    def get_packages(self) -> List[PackageDict]:
        """
        Returns all packages / plugins installed on the storage appliance
        (e.g. TrueNAS SCALE Apps, Synology packages, OpenMediaVault plugins).

        Each entry contains:

        * name (string) - package name
        * version (string) - installed or available version string
        * installed (bool) - ``True`` if the package is currently installed
        * description (string) - short package description
        * size (int) - package size in bytes; ``0`` if unknown
        * source (string) - repository or catalogue the package comes from

        Example::

            [
                {
                    "name": "plex-media-server",
                    "version": "1.40.0",
                    "installed": True,
                    "description": "Plex Media Server",
                    "size": 134217728,
                    "source": "TrueNAS Community",
                },
                {
                    "name": "nextcloud",
                    "version": "28.0.3",
                    "installed": True,
                    "description": "Nextcloud – self-hosted file sync and share",
                    "size": 268435456,
                    "source": "TrueNAS Community",
                },
            ]
        """
        raise NotImplementedError

    def install_package(self, name: str, version: str = "") -> None:
        """
        Installs a package or plugin on the storage appliance.

        :param name: Package name as known to the package catalogue.
        :param version: Exact version to install.  Empty string installs latest.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package name is unknown or the version unavailable.
        :raises RuntimeError: If the installation fails on the device side.

        Example::

            driver.install_package("nextcloud")
        """
        raise NotImplementedError

    def remove_package(self, name: str) -> None:
        """
        Removes an installed package from the storage appliance.

        :param name: Package name to remove.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not currently installed.
        :raises RuntimeError: If removal fails (e.g. required dependency).

        Example::

            driver.remove_package("plex-media-server")
        """
        raise NotImplementedError

    def get_package_config(self, name: str) -> Dict[str, Any]:
        """
        Returns the current configuration of an installed package as a dictionary.
        The structure is package-specific.

        :param name: Package name.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not installed.

        Example::

            driver.get_package_config("nextcloud")
            # →
            {
                "admin_user": "admin",
                "trusted_domains": ["nas.corp.example"],
                "mail_smtphost": "smtp.corp.example",
                "maintenance_window_start": 2,
            }
        """
        raise NotImplementedError

    def set_package_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Writes a new configuration for an installed package.

        :param name: Package name.
        :param config: New configuration as a nested dictionary.
        :raises NotImplementedError: If the driver does not support package management.
        :raises ValueError: If the package is not installed or config is invalid.
        :raises RuntimeError: If the device rejects the configuration.

        Example::

            driver.set_package_config(
                "nextcloud",
                {
                    "trusted_domains": ["nas.corp.example", "192.168.1.10"],
                    "maintenance_window_start": 3,
                },
            )
        """
        raise NotImplementedError
