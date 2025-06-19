# Collaborate on private repository with remote user

This workflow describes how you can set up a remote repository from a local
private repository.

This allows making changes remotely and getting them back to the working
repository on the desktop computer.

## On your desktop computer: Copy the working repository to a remote server

Set the environment variable `IPV4_ADDRESS` as described in
[Obtain Remote IP Address](./obtain-remote-ip-address.md).

Next, execute the following commands to copy the working repository to the
remote server:

```shell
# Clone the working repository into a bare repository
export REPO=ansible-all-my-things
git clone --bare . ~/source/$REPO.git

# Use ansible with rsync to copy the bare repository to the server
# NOTE: If nothing happens for some 10 seconds then probably the IPV4_ADDRESS
#       variable is empty. Check the ./obtain-remote-ip-address.md again.
rsync -avz --stats --progress --delete --delete-during ~/source/$REPO.git galadriel@$IPV4_ADDRESS:Documents/

# Delete the bare repository on the desktop computer
rm -rf ~/source/$REPO.git

# In my working repository, set the bare remote repository as "remote"
git remote add lorien galadriel@$IPV4_ADDRESS:Documents/$REPO.git

# Get the tracking branch for the remote repository
git pull lorien main
```

If the `.mob` configuration does not exist, then run the following setup:

```shell
mob config > .mob
```

Edit `.mob` and update the entries for

- `MOB_REMOTE_NAME` should be `lorien`
- `MOB_SKIP_CI_PUSH_OPTION_ENABLED` should be `false`

Then start mobbing.

## On the remote computer: Make changes to the repository

```shell
# Set up a git user
git config --global user.name "Stefan Boos + Claude 4-20250514 Sonnet"; \
git config --global user.email "kontakt@boos.systems"

# Clone the bare repository into a working repository
# and use the same name for the remote as on the local computer ("lorien").
# This allows using the same .mob configuration on both computers
mkdir ~/Documents/Cline
cd ~/Documents/Cline
git clone --origin lorien $REPO.git

# Checkout the mob branch
mob start

# Alternative: use a git checkout for the mob branch
git switch mob/main
```

Now make some changes.

Then use the [mob tool](https://mob.sh) or commit and push to the bare
repository.

## On your desktop computer: Bring the changes from the remote server back

In your working directory, use the [mob tool](https://mob.sh) or pull the
changes from the remote bare repository `lorien`.

## Cleanup

```shell
# Remove the "remote" from the local repository
git remote remove lorien

# Delete repositories on the remote server
rm -rf ~/Documents/$REPO.git
rm -rf ~/Documents/$REPO
```

As an alternative to cleaning up on the remote you could simply destroy it.

```shell
# Backup your configuration
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml

# Destroy
ansible-playbook ./destroy.yml
```
