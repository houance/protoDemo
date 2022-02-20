import consulate

class ConsulTool:
    def __init__(self, ip, port) -> None:
        self.consul = consulate.Consul(ip, port)

    def registerServerService(self, name, ip, port):
        self.consul.agent.service.register(
            name,
            name,
            ip,
            port,
            ['server'],
            httpcheck='http://172.30.58.167:12001',
            interval='10s',
        )

    def getLBService(self) -> list:
        allService = self.consul.agent.services()
        for service in allService:
            for v in service.values():
                if v['Tags'][0] == 'lb':
                    return [v['Address'], v['Port']]
