# Synchronize Git Repositories with a VM

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
export IPV4_ADDRESS=$(tart ip lorien); echo $IPV4_ADDRESS

# Transfer a repository to the remote
export LOCAL_REPO=$HOME/source/ansible-all-my-things
export REMOTE_USER=galadriel
export REMOTE_BARE_REPO_PARENT=/home/$REMOTE_USER/Documents
export REMOTE_CHECKOUT_PARENT=$REMOTE_BARE_REPO_PARENT/Cline
export REMOTE_NAME=lorien

./scripts/create-remote-repository.sh "$LOCAL_REPO" $REMOTE_USER $IPV4_ADDRESS "$REMOTE_BARE_REPO_PARENT" "$REMOTE_CHECKOUT_PARENT" $REMOTE_NAME
```

## Initialize mob.sh

If the `.mob` configuration does not exist, then run the following setup:

```shell
mob config > .mob
```

Edit `.mob` and update the entries for

- `MOB_REMOTE_NAME` should be `lorien`
- `MOB_SKIP_CI_PUSH_OPTION_ENABLED` should be `false`

Then start mobbing.

## On the remote computer: Make changes to the repository

Depending on which persona is driving the development, I set my git user name
and email as follows:

```shell
export SELF="Stefan Boos" \
export MODEL="Claude 4-20250514 Sonnet" \
export EMAIL=<Email address registered with my GitHub account>

git config --global user.email "$EMAIL"

# If I am driving the development, e.g. using the model's code completion
# or having a conversation with the model to craft code
git config --global user.name "$SELF + $MODEL"

# If the Model is following an implementation plan
git config --global user.name "$MODEL (+ $SELF)"

# Reset: Usually I am coding alone
git config --global user.name "$SELF"
```

The script used in the previous section has already created a clone of the
repository in the given working directory. Open the cloned folder in Visual
Studio Code and make some changes.

## On your desktop computer: Bring the changes from the remote server back

In your working directory, use the [mob tool](https://mob.sh) or pull the
changes from the remote bare repository `lorien`.

```shell
# On the remote
git push lorien

# Locally
git pull lorien main
```

## Cleanup

Make sure that the environment variables are set as described above.

Remove the remote repositories and the remote name from the local repository:

```shell
./scripts/delete-remote-repository.sh "$LOCAL_REPO" $REMOTE_USER $IPV4_ADDRESS "$REMOTE_BARE_REPO_PARENT" "$REMOTE_CHECKOUT_PARENT" $REMOTE_NAME
```

As an alternative to cleaning up on the remote you could simply destroy the
entire virtual machine.

```shell
# Backup your configuration
ansible-playbook --vault-password-file ansible-vault-password.txt ./backup.yml

# Destroy
ansible-playbook ./destroy.yml
```

---

Previous: [Work with a Virtual Machine](./work-with-vm.md)
