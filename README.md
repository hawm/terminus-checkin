# Terminus Checkin

A tool to help you do Terminus Telegram bot checkin automatically

## Usage

NOTICE: Docker installation is required! Although it may work without Docker but with your own hand.


### 1. Pull the image

```sh
docker pull akdoc/terminus-checkin
```

### 2. Checkin by run the image

Run the image will do the checkin, the first checkin needs to signing in by entering the phone number and code.

```sh
docker run -it -v telethon-sessions:/app/sessions --rm akdoc/terminus-checkin name api_id api_hash [proxy]
```

All about the command we run above:

1. `docker run`: A docker command to run the image as an executable.
2. `-it`: The first time we run checkin will need to signing in, it helps us to input the phone number and code. It can be removed after signing in, and *must* be removed when use with cron.
3. `-v telethon-sessions:/app/sessions`: Create and mount a volume to persist the Telegram session data, if not that we will need to signing in for each checkin. You can have your own volume.
4. `--rm`: Remove container after the run.
5. `akdoc/terminus-checkin` The name of Docker image we just pulled at step 1.
6. `name`: The session name be used. **Use the same name for the same Telegram account to reuse the session else you will need to signing in again.**
7. `api_id` & `api_hash`: See https://core.telegram.org/api/obtaining_api_id, **please read it carefully**.
8. `[proxy]`: This argument is optional. You can pass a proxy string to be used to communicate with Telegram. The proxy string must split with colons like
`socks:127.0.0.1:1080` or `socks:127.0.0.1:username:password:rdns`, [more info](https://docs.telethon.dev/en/stable/basic/signing-in.html#signing-in-behind-a-proxy).

In real-world example:

```sh
docker run -it -v telethon-sessions:/app/sessions --rm akdoc/terminus-checkin hello 123456789 d55761415f69af99a31e33412cb86810 socks:127.0.0.1:1080
```

### 3. Automatize with [cron](https://en.wikipedia.org/wiki/Cron)

**NOTICE**: Before automatize it, you will need to signing in once by running it manually and then entering the phone number and code. As what we do at step 2 above.

The Terminus will refresh the checkin state at every midnight of UTC+8. So combine this tool with cron so that we can checkin every day automatically.

For example, add the below content to crontab, **please note without the `-it` option**: 

```sh
0 5 * * * docker run -v telethon-sessions:/app/sessions --rm terminus-checkin name api_id api_hash [proxy]
```

It will do the checkin every day at `05:00` based on your host system timezone.

### 4. Logging(Optional)

You will want to know if the checkin is working fine, there two ways to do that is check your Telegram message or check the logs of this tool.

The tool is run by cron, so we should check the cron's logs and it's at `/var/log/syslog` by default. But it's mixed with other system logs and hard to debug and review.

So we may redirect it to our custom log file, by tail the whole command with:

```sh
>> /var/log/terminus-checkin.log 2>&1
```
[What does " 2>&1 " mean?](https://stackoverflow.com/questions/818255/what-does-21-mean)

For example:
```sh
0 5 * * * docker run -v telethon-sessions:/app/sessions --rm terminus-checkin name api_id api_hash >> /var/log/terminus-checkin.log 2>&1
```

### 5. Config Time(Optional)

Everything is working fine. But you will find this checkin tool is logging at the wrong time when you check the logs file.

That's because the dockerfile doesn't specify a timezone so it's from the original Python image.

You can specify it at runtime by bind mount the host time:

```sh
-v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro
```

For example:
```sh
0 5 * * * docker run -v telethon-sessions:/app/sessions -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro --rm terminus-checkin name api_id api_hash >> /var/log/terminus-checkin.log 2>&1
```


## Notes

- Signing in many times in a short time may be blocked by Telegram then you will need to wait a long time to be unblocked (about 80000 seconds to wait, I've been blocked when developing this tool, not sure if it blocked IP address only).
- If your account is banned(not the situation mentioned above), please see https://core.telegram.org/api/obtaining_api_id#using-the-api-id
- Checkin many times in a short time may be banned by Terminus Telegram Bot
