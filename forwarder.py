import asyncio
import logging
from time import sleep
from telethon.tl.patched import MessageService
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon import TelegramClient
from settings import API_ID, API_HASH, forwards, get_forward, update_offset


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

SENT_VIA = f'\n__Sent via__ `{str(__file__)}`'


def _(string):
    try:
        return int(string)
    except:
        return string


async def forward_job():
    async with TelegramClient('forwarder', API_ID, API_HASH) as client:
        error_occured = False
        for forward in forwards:
            from_chat, to_chat, offset = get_forward(forward)

            if not offset:
                offset = 0

            last_id = 0

            async for message in client.iter_messages(_(from_chat), reverse=True, offset_id=offset):
                if isinstance(message, MessageService):
                    continue
                try:
                    await client.forward_messages(_(to_chat), message)
                    last_id = str(message.id)
                    logging.info('forwarding message with id = %s', last_id)
                    update_offset(forward, last_id)
                except FloodWaitError as fwe:
                    print(f'\n{fwe}\n\nFloodWaitError Occured, retrying in 20 seconds.')
                    sleep(20)
                except Exception as err:
                    logging.exception(err)
                    error_occured = True
                    continue

            logging.info('Completed working with %s', forward)

        await client.send_file('me', 'config.ini', caption='This is your config file for telegram-chat-forward.')

        message = 'Your forward job has completed.' if not error_occured else 'Some errors occured. Please see the output on terminal. Contact Developer.'
        await client.send_message('me', f'''Hi !
        \n**{message}**
        \n**Telegram Chat Forward** is developed by @AahnikDaw.
        \nPlease star 🌟 on [GitHub](https://github.com/aahnik/telegram-chat-forward).
        {SENT_VIA}''', link_preview=False)

if __name__ == "__main__":
    assert forwards
    asyncio.run(forward_job())
