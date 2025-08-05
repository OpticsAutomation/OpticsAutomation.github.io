import psutil
import ctypes
import time
import os
import subprocess


# define filepaths
local_repo = r"C:\OpticsAutomation.github.io"
index_file_path = os.path.join(local_repo, "index.html")

# define locked vs. unlocked states for HTML
locked_content = '''<html><body style="display:flex;justify-content:center;align-items:center;height:100vh;margin:0;"><h1 style="color: green; text-align: center; ">OMV PC is *not* in use -- you're free to connect.</h1></body></html>'''
unlocked_content = '''<html><body style="display:flex;justify-content:center;align-items:center;height:100vh;margin:0;"><h1 style="color: red; text-align: center;">OMV PC is in use -- do not connect.</h1></body></html>'''


# checking if PC is locked
def pc_locked():
    time.sleep(10)

    user32 = ctypes.windll.user32
    hDesktop = user32.OpenInputDesktop(0, False, 0)
    if hDesktop == 0:
        # if OpenInputDesktop fails, it usually means the desktop is locked
        print("## PC is LOCKED ##")
        return True
    else:
        user32.CloseDesktop(hDesktop)

        print("## PC is UNLOCKED ##")
        return False


# interface to run Git commands
def run_git_command(command, cwd):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)


# updating the website hosted at https://opticsautomation.github.io/
def update_website(text_to_display):
    with open(index_file_path, "w") as f:
        f.write(text_to_display)

    print(f"Updated index.html at: {index_file_path}")
    print("Now adding, committing, and pushing changes to Git.")

    if text_to_display == unlocked_content:
        commit_msg = "PC now unlocked"
    else:
        commit_msg = "PC now locked"

    run_git_command(["git", "add", "index.html"], cwd=local_repo)
    run_git_command(["git", "commit", "-m", f"Update index.html state ({commit_msg}) from status_updater.py"], cwd=local_repo)
    run_git_command(["git", "push"], cwd=local_repo)


# check if the PC locked/unlocked state has changed
def fetch_pc_state_change():
    with open(index_file_path, "r") as f:
        html_content = f.read()

        if ("free to connect" in html_content) and (not pc_locked()):
            return unlocked_content
        elif ("do not connect" in html_content) and (pc_locked()):
            return locked_content
        else:
            return None


if __name__ == "__main__":
    print("Running status_updater.py")
    while True:
        pc_state_change = fetch_pc_state_change()
        print("pc_state_change:", pc_state_change)

        if pc_state_change == unlocked_content:
            update_website(unlocked_content)
            print("PC now unlocked -- updating webpage.")
        elif pc_state_change == locked_content:
            update_website(locked_content)
            print("PC is now locked -- updating webpage.")
        else:
            pass
            print("PC state is unchanged -- no actions.")

        time.sleep(10)
