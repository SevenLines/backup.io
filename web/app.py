import aiohttp_jinja2
import jinja2
from aiohttp import web

from daemon.client import ServerClient


@aiohttp_jinja2.template('index.html')
async def handle(request):
    client = ServerClient()
    await client.connect("0.0.0.0", 9997)
    await client.login(user='admin', password='bavaga5a7r=he8retruthabrama5aV')
    backups = await client.get_backups()

    return {
        'backups': backups['data']
    }

app = web.Application()
app.router.add_get('/', handle)
aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('app'))


web.run_app(app, port=8091)