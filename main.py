#!/usr/bin/env python3

# default imports
import time
import json
import subprocess

# imports that require extra installation
import typer

app = typer.Typer()


# static methods to get data from system
def get_current_cpus():
    return int(subprocess.Popen(["nproc"], stdout=subprocess.PIPE).communicate()[0])


def get_vendor():
    return str(json.loads(subprocess.Popen(["lscpu", "-J"], stdout=subprocess.PIPE).communicate()[0].decode("UTF-8)"))
               .get("lscpu")[10].get("data"))


def get_all_cpus():
    # use the native lscpu function to get core data of system
    return int(json.loads(subprocess.Popen(["lscpu", "-J"], stdout=subprocess.PIPE).communicate()[0].decode("UTF-8)"))
               .get("lscpu")[4].get("data"))


def toggle_cpus(start, end, state):
    # include the end
    for i in range(start, end):
        # state = 1 for enable 0 for disable
        with open(f"/sys/devices/system/cpu/cpu{i}/online", "wb") as f:
            subprocess.Popen(["echo", str(state)], stdout=f)


@app.command()
def disable_cpu(start: int, end: int):
    """
    Disables specified CPUs
    :param start: Starting CPU to disable
    :param end: Ending CPU to disable
    """
    try:
        if start is None or end is None:
            # this code should be unreachable as typer will error out first
            print("Start and End cannot be Empty")
        # get the total supported cpus of the installed device
        all_cpu = get_all_cpus()
        # prevent the user from killing their own system
        # it should not be possible to set cpu0 to offline
        if start == 0:
            print("You cannot disable CPU 0")
        # check if the user passed in correct values
        elif start > 0 and end <= all_cpu:
            print(f"Disabling CPUs {start} to {end} from total of {all_cpu} CPUs")
            # actually start the command
            if typer.confirm("Are you sure you want to continue?", abort=True):
                toggle_cpus(start, end, 0)
        # if the user tries to disable more CPUs than they have
        elif end > all_cpu:
            print("You cannot disable more CPUS than you have")
        # sleep to let the system catch up to our changes
        time.sleep(1)
        # gets the new CPUs value
        cur_cpu = get_current_cpus()
        print(f"You now have {cur_cpu}/{all_cpu} CPUs")
    except PermissionError:
        print("You cannot modify your system as a non root account, please re-run this command with sudo")


@app.command()
def enable_cpu(start: int, end: int):
    """
    Enables specified CPUs
    :param start: Starting CPU to enable
    :param end: Ending CPU to enable
    """
    try:
        if start is None or end is None:
            # this code should be unreachable as typer will error out first
            print("Start and End cannot be Empty")
        # get the total supported cpus of the installed device
        all_cpu = get_all_cpus()
        # check if the user passed in correct values
        if start > 0 and end <= all_cpu:
            print(f"Enabling CPUs {start} to {end}")
            # actually start the command
            if typer.confirm("Are you sure you want to continue?", abort=True):
                toggle_cpus(start, end, 1)
        # if the user tries to disable more CPUs than they have
        elif end > all_cpu:
            print("You cannot enable more CPUS than you have")
        # sleep to let the system catch up to our changes
        time.sleep(1)
        # gets the new CPUs value
        cur_cpu = get_current_cpus()
        print(f"You now have {cur_cpu}/{all_cpu} CPUs")
    except PermissionError:
        print("You cannot modify your system as a non root account, please re-run this command with sudo")


@app.command()
def disable_turbo():
    try:
        vendor = get_vendor()
        if vendor == "GenuineIntel":
            print("This command will disable turbo boost for Intel CPUs")
            if typer.confirm("Are you sure you want to continue"):
                with open(f"/sys/devices/system/cpu/intel_pstate/no_turbo", "wb") as f:
                    subprocess.Popen(["echo", 1], stdout=f)
        else:
            print(f"This feature only works with Intel CPUs, You are currently using {vendor}")
    except PermissionError:
        print("You cannot modify your system as a non root account, please re-run this command with sudo")


@app.command()
def enable_turbo():
    try:
        vendor = get_vendor()
        if vendor == "GenuineIntel":
            print("This command will disable turbo boost for Intel CPUs")
            if typer.confirm("Are you sure you want to continue"):
                with open(f"/sys/devices/system/cpu/intel_pstate/no_turbo", "wb") as f:
                    subprocess.Popen(["echo", 0], stdout=f)
        else:
            print(f"This feature only works with Intel CPUs, You are currently using {vendor}")
    except PermissionError:
        print("You cannot modify your system as a non root account, please re-run this command with sudo")


if __name__ == "__main__":
    app()
