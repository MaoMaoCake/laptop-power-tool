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
    try:
        if start is None or end is None:
            # this code should be unreachable as typer will error out first
            print("Start and End cannot be Empty")
        # get the total supported cpus of the installed device
        all_cpu = get_all_cpus()
        # prevent the user from killing their own system
        # it should not be possible to set cpu0 to offline
        if start == 0:
            print("You cannot disable Thread 0")
        # check if the user passed in correct values
        elif start > 0 and end <= all_cpu:
            print(f"Disabling cpu {start} to {end} from total of {all_cpu} Threads")
            # actually start the command
            if typer.prompt("Are you sure you want to continue? [y/n]").upper() == "Y":
                toggle_threads(start, end, 0)
            else:
                print("Operation Canceled")
                return
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



if __name__ == "__main__":
    app()
