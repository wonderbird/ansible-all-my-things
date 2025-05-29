# Collaborate on private repository with remote user

This workflow describes how you can set up a remote repository from a local
private repository.

This allows making changes remotely and getting them back to the working
repository on the desktop computer.

Outlook: Describe how to use the `mob` command in this context.

## On my desktop computer: Copy the working repository to a remote server

- clone the working repository into a bare repository
- use ansible with rsync to copy the bare repository to the server

```shell
rsync -avz --stats --progress --delete --delete-during ~/source/my-it-landscape.git galadriel@$IPV4_ADDRESS:Documents/
``` 

- delete the bare repository on the desktop computer

- in my working repository, set the bare remote repository as "remote"

```shell
git remote add remote galadriel@$IPV4_ADDRESS:Documents/my-it-landscape.git
```

## On the remote computer: Make changes to the repository

- clone the bare repository into a working repository
- make some changes
- commit and push to the bare repository

## On my desktop computer: Bring the changes from the remote server back

- in my working directory, pull the changes from the remote bare repository

## Cleanup

- remove the "remote" from the local repository

```shell
git remote remove remote
```

- delete the bare repository on the remote server
- delete the working repository on the remote server

