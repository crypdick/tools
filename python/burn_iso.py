#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "dev"
# dependencies = [
#     "typer>=0.15.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Burn an ISO file to a USB drive with safety checks and progress monitoring.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.table import Table


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
        print(f"[bold red]Error:[/bold red] getting block devices: {e}")
        raise typer.Exit(code=1)


def show_available_devices() -> None:
    """Display available block devices."""
    devices = get_block_devices()

    table = Table(title="Available Block Devices")
    table.add_column("Device", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Type")
    table.add_column("Mount Point", style="yellow")
    table.add_column("Model", style="dim")

    for device in devices.get("blockdevices", []):
        name = device.get("name", "")
        size = device.get("size", "")
        device_type = device.get("type", "")
        mountpoint = device.get("mountpoint", "") or ""
        model = device.get("model", "") or ""

        if device_type == "disk":
            table.add_row(f"/dev/{name}", size, device_type, mountpoint, model)

    print(table)


def verify_iso_file(iso_path: Path) -> None:
    """Verify the ISO file exists and is readable."""
    if not iso_path.exists():
        print(f"[bold red]Error:[/bold red] ISO file not found: {iso_path}")
        raise typer.Exit(code=1)

    if not iso_path.is_file():
        print(f"[bold red]Error:[/bold red] Path is not a file: {iso_path}")
        raise typer.Exit(code=1)

    try:
        with open(iso_path, "rb") as f:
            f.read(1024)
    except PermissionError:
        print(
            f"[bold red]Error:[/bold red] No permission to read ISO file: {iso_path}"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]Error:[/bold red] reading ISO file: {e}")
        raise typer.Exit(code=1)

    file_size_gb = iso_path.stat().st_size / (1024**3)
    print(f"[green]✓[/green] ISO file verified: {iso_path} ({file_size_gb:.2f} GB)")


def verify_usb_device(device_path: str) -> None:
    """Verify the USB device exists and is writable."""
    if not os.path.exists(device_path):
        print(f"[bold red]Error:[/bold red] Device not found: {device_path}")
        raise typer.Exit(code=1)

    try:
        result = subprocess.run(
            ["sudo", "test", "-w", device_path],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            print(
                f"[bold red]Error:[/bold red] No write permission to device: {device_path}\n"
                "Make sure you're running with sudo privileges."
            )
            raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]Error:[/bold red] checking device permissions: {e}")
        raise typer.Exit(code=1)

    print(f"[green]✓[/green] USB device verified: {device_path}")


def unmount_device_partitions(device_path: str) -> None:
    """Unmount all partitions on the device."""
    print(f"Checking for mounted partitions on {device_path}...")

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
            print(f"Found {len(mounted_partitions)} mounted partition(s)")
            for partition, mountpoint in mounted_partitions:
                print(f"Unmounting {partition} from {mountpoint}...")
                try:
                    subprocess.run(["sudo", "umount", partition], check=True)
                    print(f"[green]✓[/green] Unmounted {partition}")
                except subprocess.CalledProcessError as e:
                    print(f"[bold red]Error:[/bold red] Failed to unmount {partition}: {e}")
                    raise typer.Exit(code=1)
        else:
            print("No mounted partitions found")

    except subprocess.CalledProcessError as e:
        print(f"[bold red]Error:[/bold red] checking mounted partitions: {e}")
        raise typer.Exit(code=1)


def burn_iso_to_usb(iso_path: Path, device_path: str) -> None:
    """Burn the ISO to the USB device using dd with progress monitoring."""
    print(f"[yellow]Starting to burn {iso_path.name} to {device_path}...[/yellow]")
    print("This will take several minutes depending on USB speed.")

    cmd = [
        "sudo",
        "dd",
        f"if={iso_path}",
        f"of={device_path}",
        "bs=4M",
        "status=progress",
        "conv=fdatasync",
    ]

    print(f"Executing: {' '.join(cmd)}")

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
                print(output.strip())

        return_code = process.poll()
        if return_code != 0:
            print(f"[bold red]Error:[/bold red] dd command failed with return code {return_code}")
            raise typer.Exit(code=1)

    except KeyboardInterrupt:
        print("[bold red]Error:[/bold red] Operation cancelled by user")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"[bold red]Error:[/bold red] during burning process: {e}")
        raise typer.Exit(code=1)

    print("[green]✓[/green] Successfully burned ISO to USB!")

    print("Syncing filesystem...")
    try:
        subprocess.run(["sync"], check=True)
        print("[green]✓[/green] Sync completed")
    except subprocess.CalledProcessError as e:
        print(f"[yellow]Warning:[/yellow] Sync failed: {e}")


def main(
    iso_file: Annotated[
        Path,
        typer.Argument(
            help="Path to the ISO file to burn.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    device: Annotated[
        str,
        typer.Option(
            "--device",
            "-d",
            help="USB device path (e.g., /dev/sdb). Use --list to see available devices.",
        ),
    ] = "",
    list_devices: Annotated[
        bool,
        typer.Option("--list", help="List available block devices and exit."),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", "-n", help="Show what would be done without actually doing it."
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompts."),
    ] = False,
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

    if not device:
        print("[bold red]Error:[/bold red] --device is required. Use --list to see available devices.")
        raise typer.Exit(code=1)

    print("Current block devices:")
    show_available_devices()

    verify_iso_file(iso_file)

    if dry_run:
        if not os.path.exists(device):
            print(f"[bold red]Error:[/bold red] Device not found: {device}")
            raise typer.Exit(code=1)
        print(f"[green]✓[/green] USB device exists: {device}")
    else:
        verify_usb_device(device)

    print("\n[bold]Operation Summary:[/bold]")
    print(f"  ISO file: {iso_file} ({iso_file.stat().st_size / (1024**3):.2f} GB)")
    print(f"  Target device: {device}")

    if dry_run:
        print("\n[yellow bold]🔍 DRY RUN MODE - No changes will be made![/yellow bold]")
        print("The following operations would be performed:")
        print(f"  1. Check and unmount any partitions on {device}")
        print(f"  2. Write {iso_file.name} to {device} using dd with 4MB blocks")
        print("  3. Sync filesystem to ensure data integrity")
        print("\n[green]✓[/green] Dry run completed - everything looks good!")
        print("To actually burn the ISO, run without --dry-run flag.")
        return

    if not force:
        print(
            f"\n[red bold]⚠️  WARNING: This will completely erase all data on {device}![/red bold]"
        )
        if not typer.confirm("\nAre you absolutely sure you want to continue?"):
            print("Operation cancelled.")
            return

    unmount_device_partitions(device)
    burn_iso_to_usb(iso_file, device)

    print("\n[green bold]✓ ISO successfully burned to USB![/green bold]")
    print(f"Your USB drive at {device} is now bootable.")


if __name__ == "__main__":
    typer.run(main)
