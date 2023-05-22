#!/bin/bash

RCLONE_CONFIG=/home/raph/.config/rclone/rclone.conf
export RCLONE_CONFIG

local_dir="/temp"
remote_dir="dbxcrypt:"

function upload() {
    echo "Moving ${local_dir}/ to ${remote_dir}..."
    /usr/bin/rclone move \
        "${local_dir}/" "${remote_dir}" \
        --log-file /var/log/rclone/upload.log \
        -v \
        --exclude-from /home/raph/scripts/excludes \
        --delete-empty-src-dirs \
        --fast-list \
        --dropbox-chunk-size 120M \
        --tpslimit-burst 12 \
        --transfers 6 \
        --stats-one-line
        --min-age 1h
    echo "Complete!"
}

upload
