# run with docker run -it --privileged debian

mountPoint='ext4mount'
mkdir "$mountPoint"
size=1M
name=nested-tar-and-symlink-$size.ext4
dd if=/dev/zero of="$name" bs="$size" count=1
mkfs.ext4 "$name"
mount -o loop "$name" "$mountPoint"  # Still not possible without sudo :(
(
    cd "$mountPoint" &&
    rmdir --ignore-fail-on-non-empty 'lost+found' &&
    chmod a+rwx . &&
    mkdir -p foo &&
    cd foo &&
    echo Hi > bar &&
    ln -s bar BAR &&
    cd .. &&
    tar -cf foo.tar foo
)
umount "$mountPoint"
rmdir "$mountPoint"

# Copied out with: docker container cp 1234567abcd:/nested-tar-and-symlink-1M.ext4 .
