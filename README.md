# media-server
Overview of home media server setup, including architecture, workflow, and automation scripts.

## rclone Setup

### dbx

To get your `client_id` and `client_secret`, follow rclone's guide to [Get your own Dropbox App ID](https://rclone.org/dropbox/#get-your-own-dropbox-app-id).
```
e/n/d/r/c/s/q> n
name> dbx
Storage> 13 (dropbox)
client_id>
client_secret>
edit advanced config> n
```

### dbxcrypt
```
e/n/d/r/c/s/q>
name> dbxcrypt
Storage> 14 (crypt)
remote> dbx:
filename_encryption> 1 (standard)
directory_name_encryption> 1 (true)
password for encryption>
password2 for encryption>
edit advanced config> n
```

## High-Level Architecture
![](./blob/media_server.png)

## Mounts and Drives Info

- [/dbx](./etc/systemd/system/dbx.service) - encrypted rclone mount
- [/media](./etc/systemd/system/media.service) - mergerfs mount for mounts `/temp:/dbx`
- /downloads - NVME
- /temp - HDD
- /transcode - HDD

## Workflow
1. Mount [/dbx](./etc/systemd/system/dbx.service).
2. Mount [/media](./etc/systemd/system/media.service). Sonarr/Radarr and Plex/Emby all read from `/media`.
3. NZBGet/Sabnzbd downloads to `/downloads`.
4. Sonarr/Radarr post-processes files in `/downloads` and moves them to `/temp`.
5. [upload.timer](./etc/systemd/system/upload.timer) triggers the [upload.service](./etc/systemd/system/upload.service) daily, which runs the [upload.sh](./scripts/upload.sh) script to move files from `/temp` to `/dbx`.
