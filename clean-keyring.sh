#!/bin/bash
# Clean up the GPG Keyring.  Keep it tidy.
# www.lavall.ee
#
# Modified by Roland Smith.
# Last modified: 2015-05-09 15:09:30 +0200

echo -n "Expired Keys: "
for expiredKey in $(gpg2 -k | awk '/^pub.* \[expired\: / {id=$2; sub(/^.*\//, "", id); print id}'); do
    echo -n "$expiredKey"
    gpg2 --batch --yes --delete-keys $expiredKey >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -n "(OK), "
    else
        echo -n "(FAIL), "
    fi
done
echo done.

echo -n "Update Keys: "
for keyid in $(gpg2 -k | awk '/^pub/&&!(/revoked\:/||/expired\:/) {id=$2; sub(/^.*\//, "", id); print id}'); do
    echo -n "$keyid"
    gpg2 --batch --quiet --edit-key "$keyid" check clean cross-certify save quit > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -n "(OK), "
    else
        echo -n "(FAIL), "
    fi
done
echo done.

gpg2 --batch --quiet --refresh-keys > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Refresh OK"
else
     echo "Refresh FAIL."
fi
