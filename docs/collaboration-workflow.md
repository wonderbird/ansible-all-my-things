# Collaborate on private repository with remote user

This workflow describes how you can set up a remote repository from a local
private repository.

This allows making changes remotely and getting them back to the working
repository on the desktop computer.

Outlook: Describe how to use the `mob` command in this context.

## On my desktop computer: Copy the working repository to a remote server

```shell
# Assign the IPv4 address of the remote server to a variable
export IPV4_ADDRESS=$(tart ip lorien)

# Clone the working repository into a bare repository
git clone --bare . ~/source/my-it-landscape.git

# Use ansible with rsync to copy the bare repository to the server
rsync -avz --stats --progress --delete --delete-during ~/source/my-it-landscape.git galadriel@$IPV4_ADDRESS:Documents/

# Delete the bare repository on the desktop computer
rm -rf ~/source/my-it-landscape.git

# In my working repository, set the bare remote repository as "remote"
git remote add lorien galadriel@$IPV4_ADDRESS:Documents/my-it-landscape.git

# Get the tracking branch for the remote repository
git pull lorien main

# Configure mob.sh to use the remote
mob config > .mob
```

Finally, edit `.mob` and update the entries for

- `MOB_REMOTE_NAME`
- `MOB_SKIP_CI_PUSH_OPTION_ENABLED`

Then start mobbing.

## On the remote computer: Make changes to the repository

```shell
# Set up a git user
git config --global user.name "Galadriel"
git config --global user.email "galadriel@middle-earth.com"

# Clone the bare repository into a working repository
# and use the same name for the remote as on the local computer ("lorien").
# This allows using the same .mob configuration on both computers
git clone --origin lorien my-it-landscape.git

# Checkout the mob branch
mob start

# Alternative: use a git checkout for the mob branch
git switch mob/main
```

- Make some changes
- Commit and push to the bare repository

## On my desktop computer: Bring the changes from the remote server back

- In my working directory, pull the changes from the remote bare repository

## Cleanup

```shell
# Remove the "remote" from the local repository
git remote remove lorien

# Delete repositories on the remote server
rm -rf ~/Documents/my-it-landscape.git
rm -rf ~/Documents/my-it-landscape
```

As an alternative to cleaning up on the remote you could simply destroy it.

```shell
ansible-playbook ./destroy.yml
```
