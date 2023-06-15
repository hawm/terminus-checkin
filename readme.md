# Terminus Checkin

A tool to help you do Terminus Telegram bot checkin

## Usage

NOTES: Docker installation is required! Although it may work without Docker but with your own hand.


### 1. Pull the image

```sh
docker pull akdoc/terminus-checkin
```

### 2. Checkin by run the image

Run the image will do the checkin, the first checkin needs to signing in by entering the phone number and code.

```sh
docker run -it -v sessions:/app/sessions --rm akdoc/terminus-checkin name api_id api_hash [proxy]
```

All about the command we run above:

1. `docker run`: A docker command to run the image as an executable.
2. `-it`: The first time we run checkin will need to signing in, it helps us to input the phone number and code. It can be removed after signing in.
3. `-v sessions:/app/sessions`: Create and mount a volume to save the session data, if not that we will need to signing in for each checkin. You can have your own volume.
4. `--rm`: Remove the container after the run.
5. `akdoc/terminus-checkin` The Docker image name we just pulled at step 1.
6. `name`: The session name be used. Use the same name for the same Telegram account to reuse the session else you will need to signing in again.
7. `api_id` & `api_hash`: See https://core.telegram.org/api/obtaining_api_id
8. `[proxy]`: This argument is optional. You can pass a proxy string to be used to communicate with Telegram. The proxy string must split with colons like
`socks:127.0.0.1:1080` or `socks:127.0.0.1:username:password:rdns`, [more info](https://docs.telethon.dev/en/stable/basic/signing-in.html#signing-in-behind-a-proxy).

In real-world example:

```sh
docker run -it -v sessions:/app/sessions --rm akdoc/terminus-checkin hello 123456789 d55761415f69af99a31e33412cb86810 socks:127.0.0.1:1080
```

### 3. Automatize with Crontab

**NOTES**: Before automatize it, you need to signing in once by running it manually and then entering the phone number and code.

The Terminus will refresh the checkin state at every midnight of UTC+8. So combine this tool with Crontab so that we can checkin every day automatically.

For example, add the below content to Crontab, please note without the `-it` option: 

```sh
0 5 * * * docker run -v sessions:/app/sessions --rm terminus-checkin name api_id api_hash [proxy]
```

It will do the checkin every day at `05:00` based on your system timezone.

### 4. Logging(Optional)

You will want to know if the checkin is working fine, there two ways to do that is check your Telegram message or check the logs of this tool.

The tool is run by Crontab, so we should check the crontab's logs and it's at `/var/log/syslog` by default. But you know it's confused with other system logs.

So we redirect it to our custom log file. By tail the whole command with:
```sh
>> /var/log/terminus-checkin.log 2>&1
```

For example:
```sh
0 5 * * * docker run -v sessions:/app/sessions --rm terminus-checkin name api_id api_hash >> /var/log/terminus-checkin.log 2>&1
```

### 5. Config Time(Optional)

Everything is fine. But you will find this checkin tool is logging at the wrong time.

That's because the dockerfile doesn't specify a timezone so it's from the original Python image.

You can specify it at runtime by bind mount the host time:

```sh
-v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro
```

For example:
```sh
0 5 * * * docker run -v sessions:/app/sessions -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --rm terminus-checkin name api_id api_hash >> /var/log/terminus-checkin.log 2>&1
```


## Notes

- Signing in many times in a short time may be blocked by Telegram then you will need to wait a long time to be unblocked (about 80000 seconds to wait, I've been blocked when developing this tool, not sure if it blocked IP address only).
- If your account is banned(not the situation mentioned above), please see https://core.telegram.org/api/obtaining_api_id#using-the-api-id
- Checkin many times in a short time may be blocked by Terminus Telegram Bot
