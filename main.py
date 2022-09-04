#!/usr/bin/env python3

# default imports
import time
import json
import subprocess

# imports that require extra installation
import typer

app = typer.Typer()


def get_current_cpus():
    return int(subprocess.Popen(["nproc"], stdout=subprocess.PIPE).communicate()[0])


def get_all_cpus():
    # use the native lscpu function to get core data of system
    return int(json.loads(subprocess.Popen(["lscpu", "-J"], stdout=subprocess.PIPE).communicate()[0].decode("UTF-8)"))
               .get("lscpu")[4].get("data"))


def toggle_threads(start, end, state):
    # include the end
    for i in range(start, end):
        # state = 1 for enable 0 for disable
        with open(f"/sys/devices/system/cpu/cpu{i}/online", "wb") as f:
            subprocess.Popen(["echo", str(state)], stdout=f)


@app.command()
def disable_thread(start: int, end: int):
    """
    Disables specified threads
    :param start: starting Thread to disable
    :param end: Ending Thread to disable
    """
    # check the number of processing units(threads)
    if start is None or end is None:
        # this code should be unreachable as typer will error out first
        print("Start and End cannot be Empty")
    all_cpu = get_all_cpus()
    if start == 0:
        print("You cannot disable Thread 0")
    elif start > 0 and end <= all_cpu:
        print(f"Disabling cpu {start} to {end} from total of {all_cpu} Threads")
        toggle_threads(start, end, 0)
    elif end > all_cpu:
        print("You Cannot disable more CPUS than you have")
    cur_cpu = get_current_cpus()
    print(f"You now have {cur_cpu}/{all_cpu} CPUs")


@app.command()
def enable_thread(start: int = 1, end: int = 1):
    cur_cpu = get_current_cpus()
    if start == 0:
        print("You cannot disable Thread 0")
    elif start > 0:
        print(f"Enabling Threads {start} to {end}")
        toggle_threads(start, end, 1)


if __name__ == "__main__":
    app()
