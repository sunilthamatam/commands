import os, sys, subprocess
import urllib2

LAST_N_COMMITS = 50
DEV_NULL = open(os.devnull, 'w')
CHECKSTYLE_JAR = "https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.22/checkstyle-8.22-all.jar"
CHECKSTYLE_JAR_PATH = "/tmp/checkstyle-8.22-all.jar"
CHECKSTYLE_CONFIG = "checkstyle.xml"


def main(args):

    """
        Check if git context exists
    """
    branch_name = get_branch_name()
    if branch_name is None:
        print("No git branch exists")
        exit(0)

    download_checkstyle_jar()

    files_modified = get_modified_files()
    """
        Run checkstyle on modified files
    """
    run_checkstyle(files_modified)


def run_checkstyle(modified_files):

    for modified_file in modified_files:

        msg = "Running on source file : " + modified_file
        msg_delim = "+" * len(msg)
        print(msg_delim)
        print(msg)
        print(msg_delim)

        checkstyle_cmd = [
            "java",
            "-jar",
            CHECKSTYLE_JAR_PATH,
            "-c",
            CHECKSTYLE_CONFIG,
            modified_file
        ]
        checkstyle_proc = subprocess.Popen(checkstyle_cmd, stdout=sys.stdout)
        checkstyle_proc.wait()

        print("-" * len(msg))


def download_checkstyle_jar():
    if os.path.exists(CHECKSTYLE_JAR_PATH):
        print("")
        print("Found checkstyle jar at " + CHECKSTYLE_JAR_PATH)
        print("")
        return

    print("Downloading checkstyle-8.22-all.jar ... ")

    u = urllib2.urlopen(CHECKSTYLE_JAR)
    with open(CHECKSTYLE_JAR_PATH, "wb") as output:
        output.write(u.read())

    print("Download complete.")


def get_modified_files():

    modified_files = []

    """
        fetch modified files from user commits
    """
    user_commits = get_user_commits()

    git_committed_cmd = [
        "git",
        "diff",
        "--name-only",
        "HEAD",
        "HEAD~" + str(user_commits)
    ]

    git_committed_proc = subprocess.Popen(git_committed_cmd, stdout=subprocess.PIPE)

    for git_file in iter(git_committed_proc.stdout.readline, ''):
        git_file = git_file.strip('\n')
        if git_file.find(".java") > 0:
            modified_files.append(git_file)

    """ 
        fetch modified uncommitted files
    """
    branch_name = get_branch_name()
    git_uncommitted_cmd = [
        "git",
        "diff",
        "--name-only",
        "origin/" + branch_name
    ]

    git_uncommitted_proc = subprocess.Popen(git_uncommitted_cmd, stdout=subprocess.PIPE)

    for git_file in iter(git_uncommitted_proc.stdout.readline, ''):
        git_file = git_file.strip('\n')
        if git_file.endswith(".java"):
            modified_files.append(git_file)

    return set(modified_files)


def get_user_commits():
    git_log_cmd = [
        "git",
        "log",
        "--pretty=oneline",
        "--abbrev-commit",
        "-" + str(LAST_N_COMMITS)
    ]

    git_log_proc = subprocess.Popen(git_log_cmd, stdout=subprocess.PIPE)
    git_log_proc.wait()

    commit_counter = 0

    for line in iter(git_log_proc.stdout.readline, ''):
        commit_counter = commit_counter + 1

        if line.find(" [job-creator]") > 0:
            break

    return commit_counter


def get_branch_name():
    git_branch_cmd = [
        "git",
        "rev-parse",
        "--abbrev-ref",
        "HEAD"
    ]

    git_branch_proc = subprocess.Popen(git_branch_cmd, stdout=subprocess.PIPE, stderr=DEV_NULL)
    git_branch_proc.wait()

    if git_branch_proc.returncode == 0:
        return git_branch_proc.stdout.readline().strip('\n')


if __name__ == "__main__":
    main(sys.argv)
else:
    print("call main() function")