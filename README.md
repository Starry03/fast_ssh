# Fast SSH

Simple cli tool to replace termius trash desktop apps

## Quickstart

```sh
git clone https://github.com/Starry03/fast_ssh
cd fast_ssh
./scripts/install.sh # build + installation
```

## How to use it

### First time run

```sh
fast_ssh
```

will ask you to insert a master password (cannot be recovered)

### Add/remove connections

```sh
fast_ssh --add <name> <ip> <username> <password>
```
password will be encrypted and stored into sql lite

```sh
fast_ssh --remove <name>
```

### List connections

```sh
fast_ssh --list
```

