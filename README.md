# Fast SSH

Simple cli tool to replace termius trash desktop apps

## Jumpstart

```sh
./scripts/build.sh
```

will go into `./dist/main`

## How to use it

### First time run

```sh
./dist/main
```

will ask you to insert a master password

### Add/remove connections

```sh
./dist/main --add-host <name> <ip> <username> <password>
```
password will be encrypted and stored into sql lite

```sh
./dist/main --remove-host <name> <ip> <username> <password>
```

