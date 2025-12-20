#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "dev"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///
"""
Burn an ISO file to a USB drive with safety checks and progress monitoring.
"""

import json
import os
import subprocess
from pathlib import Path

import click


def get_block_devices() -> dict:
    """Get list of block devices with their info."""
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,MODEL", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Error getting block devices: {e}") from e


def show_available_devices() -> None:
    """Display available block devices."""
    devices = get_block_devices()

    click.echo("\nAvailable Block Devices:")
    click.echo("-" * 70)
    click.echo(f"{'Device':<12} {'Size':<10} {'Type':<8} {'Mount Point':<20} {'Model'}")
    click.echo("-" * 70)

    for device in devices.get("blockdevices", []):
        name = device.get("name", "")
        size = device.get("size", "")
        device_type = device.get("type", "")
        mountpoint = device.get("mountpoint", "") or ""
        model = device.get("model", "") or ""

        if device_type == "disk":
            click.echo(f"/dev/{name:<8} {size:<10} {device_type:<8} {mountpoint:<20} {model}")

    click.echo("-" * 70)


def verify_iso_file(iso_path: Path) -> None:
    """Verify the ISO file exists and is readable."""
    if not iso_path.exists():
        raise click.ClickException(f"ISO file not found: {iso_path}")

    if not iso_path.is_file():
        raise click.ClickException(f"Path is not a file: {iso_path}")

    try:
        with open(iso_path, "rb") as f:
            f.read(1024)
    except PermissionError as e:
        raise click.ClickException(f"No permission to read ISO file: {iso_path}") from e
    except Exception as e:
        raise click.ClickException(f"Error reading ISO file: {e}") from e

    file_size_gb = iso_path.stat().st_size / (1024**3)
    click.secho(f"✓ ISO file verified: {iso_path} ({file_size_gb:.2f} GB)", fg="green")


def verify_usb_device(device_path: str) -> None:
    """Verify the USB device exists and is writable."""
    if not os.path.exists(device_path):
        raise click.ClickException(f"Device not found: {device_path}")

    try:
        result = subprocess.run(
            ["sudo", "test", "-w", device_path],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise click.ClickException(
                f"No write permission to device: {device_path}\n"
                "Make sure you're running with sudo privileges."
            )
    except Exception as e:
        raise click.ClickException(f"Error checking device permissions: {e}") from e

    click.secho(f"✓ USB device verified: {device_path}", fg="green")


def unmount_device_partitions(device_path: str) -> None:
    """Unmount all partitions on the device."""
    click.echo(f"Checking for mounted partitions on {device_path}...")

    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,MOUNTPOINT", "-n", device_path],
            capture_output=True,
            text=True,
            check=True,
        )

        mounted_partitions = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2 and parts[1] != "":
                    partition_name = parts[0].strip("├─└─│ ")
                    mountpoint = parts[1]
                    mounted_partitions.append((f"/dev/{partition_name}", mountpoint))

        if mounted_partitions:
            click.echo(f"Found {len(mounted_partitions)} mounted partition(s)")
            for partition, mountpoint in mounted_partitions:
                click.echo(f"Unmounting {partition} from {mountpoint}...")
                try:
                    subprocess.run(["sudo", "umount", partition], check=True)
                    click.secho(f"✓ Unmounted {partition}", fg="green")
                except subprocess.CalledProcessError as e:
                    raise click.ClickException(f"Failed to unmount {partition}: {e}") from e
        else:
            click.echo("No mounted partitions found")

    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"Error checking mounted partitions: {e}") from e


def burn_iso_to_usb(iso_path: Path, device_path: str) -> None:
    """Burn the ISO to the USB device using dd with progress monitoring."""
    click.secho(f"Starting to burn {iso_path.name} to {device_path}...", fg="yellow")
    click.echo("This will take several minutes depending on USB speed.")

    cmd = [
        "sudo",
        "dd",
        f"if={iso_path}",
        f"of={device_path}",
        "bs=4M",
        "status=progress",
        "conv=fdatasync",
    ]

    click.echo(f"Executing: {' '.join(cmd)}")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                click.echo(output.strip())

        return_code = process.poll()
        if return_code != 0:
            raise click.ClickException(f"dd command failed with return code {return_code}")

    except KeyboardInterrupt:
        raise click.ClickException("Operation cancelled by user")
    except Exception as e:
        raise click.ClickException(f"Error during burning process: {e}") from e

    click.secho("✓ Successfully burned ISO to USB!", fg="green")

    click.echo("Syncing filesystem...")
    try:
        subprocess.run(["sync"], check=True)
        click.secho("✓ Sync completed", fg="green")
    except subprocess.CalledProcessError as e:
        click.secho(f"Warning: Sync failed: {e}", fg="yellow")


@click.command()
@click.argument(
    "iso_file",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option(
    "--device",
    "-d",
    required=True,
    help="USB device path (e.g., /dev/sdb). Use --list to see available devices.",
)
@click.option(
    "--list",
    "list_devices",
    is_flag=True,
    help="List available block devices and exit.",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be done without actually doing it.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Skip confirmation prompts.",
)
def main(
    iso_file: str,
    device: str,
    list_devices: bool,
    dry_run: bool,
    force: bool,
) -> None:
    """
    Burn an ISO file to a USB drive with safety checks and progress monitoring.

    This tool will verify the ISO file, check the target device, unmount any
    mounted partitions, and burn the ISO using dd with progress reporting.

    DANGER: This will completely erase all data on the target USB device!

    Arguments:

        ISO_FILE: Path to the ISO file to burn.

    Examples:

        uv run https://tools.ricardodecal.com/python/burn_iso.py --list

        uv run https://tools.ricardodecal.com/python/burn_iso.py ubuntu.iso --device /dev/sdb --dry-run

        uv run https://tools.ricardodecal.com/python/burn_iso.py ~/Downloads/debian.iso -d /dev/sdc
    """
    if list_devices:
        show_available_devices()
        return

    iso_path = Path(iso_file).expanduser().resolve()

    click.echo("Current block devices:")
    show_available_devices()

    verify_iso_file(iso_path)

    if dry_run:
        if not os.path.exists(device):
            raise click.ClickException(f"Device not found: {device}")
        click.secho(f"✓ USB device exists: {device}", fg="green")
    else:
        verify_usb_device(device)

    click.echo(f"\nOperation Summary:")
    click.echo(f"  ISO file: {iso_path} ({iso_path.stat().st_size / (1024**3):.2f} GB)")
    click.echo(f"  Target device: {device}")

    if dry_run:
        click.secho("\n🔍 DRY RUN MODE - No changes will be made!", fg="yellow", bold=True)
        click.echo("The following operations would be performed:")
        click.echo(f"  1. Check and unmount any partitions on {device}")
        click.echo(f"  2. Write {iso_path.name} to {device} using dd with 4MB blocks")
        click.echo("  3. Sync filesystem to ensure data integrity")
        click.secho("\n✓ Dry run completed - everything looks good!", fg="green")
        click.echo("To actually burn the ISO, run without --dry-run flag.")
        return

    if not force:
        click.secho(
            f"\n⚠️  WARNING: This will completely erase all data on {device}!",
            fg="red",
            bold=True,
        )
        if not click.confirm("\nAre you absolutely sure you want to continue?"):
            click.echo("Operation cancelled.")
            return

    unmount_device_partitions(device)
    burn_iso_to_usb(iso_path, device)

    click.secho("\n✓ ISO successfully burned to USB!", fg="green", bold=True)
    click.echo(f"Your USB drive at {device} is now bootable.")


if __name__ == "__main__":
    main()

