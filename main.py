import argparse

from app import App


def main():
    parser = argparse.ArgumentParser(description="Choose the ssh, with auto-login")
    parser.add_argument("--add", nargs=4, metavar=("NAME", "IP", "USERNAME", "PASSWORD"),
                        help="Add a new host to the database")
    parser.add_argument("--list", action="store_true", help="List all hosts in the database")
    parser.add_argument("--remove", metavar="ID", help="Remove a host from the database by name")
    parser.add_argument("--reset", action="store_true",
                        help="Reset the master password (will require re-entering all host information)")
    parser.add_argument("--version", action="version", version="%(prog)s 1.1")
    parser.add_argument("--timeout", metavar="SECONDS", type=int, help="Timeout (seconds)")

    args = parser.parse_args()
    app = App(args)
    app.setup()
    if not args.list:
        app.core()

if __name__ == "__main__":
    main()
