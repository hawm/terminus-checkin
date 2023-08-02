"""Terminus Checkin
"""
import logging
import sys
from asyncio import sleep
from typing import Any
from telethon import TelegramClient, events
from telethon.tl.custom.message import Message
import ddddocr

BOT_USERNAME = 'EmbyPublicBot'


class TerminusCheckin():
    '''Terminus Checkin'''
    @staticmethod
    def img2txt(img: bytes) -> str:
        '''Recogize captcha image to text'''
        ocr = ddddocr.DdddOcr(show_ad=False)
        text = ocr.classification(img)
        return text

    @staticmethod
    def get_logger(name: str):
        '''Return a logger'''
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    CHECKIN_MESSAGE = '/checkin'
    CANCEL_MESSAGE = '/cancel'

    timeout = 15
    retry_interval = 30
    retry_max = 3

    _retry_count = 0
    _retry_flag = False

    def __init__(self, name: str, app_id: int, app_hash: str,
                 proxy: tuple | dict | None = None):
        self.logger = self.get_logger('Terminus Checkin')
        self.logger.debug('Logger setup')
        self.logger.debug('Init Telegram client')
        self.client = TelegramClient(f'./sessions/{name}', app_id,
                                     app_hash, proxy=proxy)  # type: ignore
        self._load_event_handler()

    def _load_event_handler(self):
        '''Add event handler to client'''
        self.logger.debug('Load event handlers')
        for name in dir(self):
            attr = getattr(self, name)
            if events.is_handler(attr):
                self.logger.debug('Load event handler %s', name)
                self.client.add_event_handler(attr)
        self.logger.debug('Load event handlers finished')

    async def _async_img2txt(self, img: bytes) -> str:
        self.logger.debug('Image parsing')
        text = await self.client.loop.run_in_executor(None, self.img2txt, img)
        self.logger.debug('Image recogize as %s', text)
        return text

    def start(self):
        '''Start checkin'''
        self.client.loop.run_until_complete(self._start())

    async def _start(self):
        self.logger.info('Checkin start')
        try:
            async with self.client:
                self.logger.info('Authed Telegram account')
                await self._checkin()
        except KeyboardInterrupt:
            print('\n')
            self.logger.info('Stop by user')
        except EOFError:
            print('\n')
            self.logger.warning('Stop by system')
        except Exception as error:
            self.logger.error(error)
        finally:
            self.logger.info('Checkin end')

    def _set_retry(self):
        self.logger.info('Retry flag has been set')
        self._retry_flag = True

    async def _retry(self):
        if not self._retry_flag:
            return
        self._retry_flag = False

        if self._retry_count < self.retry_max:
            self.logger.info('Wait %ss to retry', self.retry_interval)
            await sleep(self.retry_interval)
            self._retry_count += 1
            self.logger.info('The %s retry start', self._retry_count)
            await self._checkin()
        else:
            self.logger.warning('Max retry exceeded')

    async def _checkin(self):
        '''Start checkin by cancel any existing session'''
        await self._cancel()
        # wait for events
        await sleep(self.timeout)
        # do possible retry
        await self._retry()

    async def _cancel(self):
        '''Cancel any existing session'''
        self.logger.info('Send cancel message')
        await self.client.send_message(BOT_USERNAME, self.CANCEL_MESSAGE)

    @events.register(events.NewMessage(chats=BOT_USERNAME, pattern='.*(会话已取消|无需清理)'))
    async def _checkin_start(self, event: events.NewMessage.Event):
        '''Trigger checkin process'''
        self.logger.info('Receive session cleared message')
        self.logger.info('Send checkin message')
        await event.message.respond(self.CHECKIN_MESSAGE)

    @events.register(events.NewMessage(chats=BOT_USERNAME, pattern='.*输入签到验证码'))
    async def _checkin_verify(self, event: events.NewMessage.Event):
        self.logger.info('Receive captcha message')
        message: Message = event.message
        image = await message.download_media(file=bytes)
        if not image:
            self.logger.info('Captcha image not found')
            self._set_retry()
            return
        self.logger.info('Captcha image found')
        text = await self._async_img2txt(image)
        if text.startswith('/'):
            self.logger.info('Captcha recogize error: start with `/`')
            self._set_retry()
            return
        self.logger.info('Captcha recogized')
        self.logger.info('Send captcha verify message')
        await message.respond(text)

    @events.register(events.NewMessage(chats=BOT_USERNAME, pattern='.*签到验证码输入错误或超时'))
    async def _checkin_failed(self, event: events.NewMessage.Event):
        self.logger.info('Receive captcha mismatch or timeout message')
        self.logger.info('Checkin failed')
        self._set_retry()

    @events.register(events.NewMessage(chats=BOT_USERNAME, pattern='.*你今天已经签到过了'))
    async def _checkin_already(self, event: events.NewMessage.Event):
        self.logger.info('Receive checkin already message')
        self.logger.info('Checkin already')

    @events.register(events.NewMessage(chats=BOT_USERNAME, pattern='.*签到成功'))
    async def _checkin_succeed(self, event: events.NewMessage.Event):
        self.logger.info('Receive checkin success message')
        self.logger.info('Checkin succeed')

    @events.register(events.NewMessage(chats=BOT_USERNAME, pattern='.*请勿高频使用厂妹'))
    async def _checkin_banned(self, event: events.NewMessage.Event):
        self.logger.info('Receive checkin banned message')
        self.logger.info('Checkin banned')


if __name__ == '__main__':
    args = sys.argv[1:]
    argc = len(args)
    if argc == 3:
        args.append('')
    elif argc == 4:
        pass
    else:
        print(f'Arguments number must be 3 or 4, but got {argc}')
        print('Usage: python checkin.py name api_id api_hash [proxy]')
        sys.exit(1)

    name, api_id, api_hash, proxy = args

    api_id = int(api_id, 10)
    proxyt = None

    if proxy:
        proxyl: list[Any] = proxy.split(':')
        proxyc = len(proxyl)
        if proxyc not in range(3, 6):
            print('Proxy string invalid')
            print('Must split with colons and at least 3 component')
            print('socks5:127.0.0.1:1080')
            print('socks5:127.0.0.1:1080:username:password:rdns')
            sys.exit(1)
        proxyl[2] = int(proxyl[2])
        if proxyc == 5:
            proxyl[4] = not proxyl[4].lower() == 'false'
        proxyt = tuple(proxyl)

    TerminusCheckin(name, api_id, api_hash, proxy=proxyt).start()
