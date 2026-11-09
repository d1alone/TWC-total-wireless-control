# Contribuindo com o TWC

Obrigado por considerar uma contribuição.

## Antes de começar

- Abra uma issue para discutir mudanças maiores antes de implementá-las.
- Relate erros incluindo a distribuição/versão, ambiente gráfico, adaptador e
  driver quando souber, passos para reproduzir e mensagens relevantes do log.
- Não inclua senhas, dados pessoais, endereços MAC ou outras informações
  sensíveis em issues e logs.

## Alterações de código

- Mantenha compatibilidade com Python 3 e siga o estilo existente.
- Prefira comandos diretos com listas de argumentos; não construa comandos
  shell com texto de entrada.
- Preserve a confirmação antes de ações que possam desconectar a rede ou parar
  serviços.
- Atualize a documentação, o changelog Debian e a versão do pacote quando
  apropriado.
- Não adicione dependências sem explicar sua necessidade.

## Verificações locais

```sh
PYTHONPYCACHEPREFIX=/tmp/twc-pycache python3 -m py_compile twc.py
desktop-file-validate debian/twc.desktop
./build-deb.sh /tmp/twc.deb
dpkg-deb --info /tmp/twc.deb
```

O teste de interface requer uma sessão gráfica. Ações administrativas devem
ser verificadas somente em uma máquina de teste ou interface que você esteja
autorizado a administrar.

## Pull requests

Explique o problema, a solução, como validou a mudança e eventuais efeitos na
conectividade ou nos privilégios. Inclua capturas de tela quando a interface
for alterada, sem mostrar informação pessoal.

Todas as contribuições distribuídas com o projeto ficam sob GPL-3.0-or-later.
