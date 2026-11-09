# TWC — Total Wireless Control

Aplicativo gráfico para controlar interfaces Wi-Fi locais em distribuições
Linux baseadas em Debian, como Linux Mint e Kali Linux.

**Idealizado por Benyvan (@benyvan).**
**Licença:** GNU General Public License v3.0 ou posterior
(GPL-3.0-or-later).

> O TWC é uma ferramenta administrativa avançada. Depois da autenticação,
> toda a aplicação roda como `root`. Use somente em computadores e interfaces
> que você tem autorização para administrar.

## Recursos

- Detecta interfaces wireless disponíveis e permite atualizar a lista.
- Sobe e desce uma interface.
- Alterna entre os modos `monitor` e `managed`.
- Mostra o estado da interface com um teste de leitura usando `iw`.
- Pode parar processos que interferem com o modo monitor (`airmon-ng check
  kill`).
- Pode parar ou reiniciar o NetworkManager, sempre pedindo confirmação.
- Exibe comandos e resultados em um log que pode ser selecionado e copiado.
- Usa o ícone TWC no lançador e na janela do aplicativo.

## Requisitos

- Linux com ambiente gráfico e uma sessão ativa (X11 ou Wayland)
- Python 3 e Tkinter
- PolicyKit (`pkexec`) e um agente de autenticação gráfica
- `iw`, `iproute2`, `aircrack-ng`
- NetworkManager e `systemctl` para os controles correspondentes

No Linux Mint, instale os requisitos com:

```sh
sudo apt update
sudo apt install python3 python3-tk policykit-1 iw iproute2 aircrack-ng network-manager
```

No Kali Linux, o mesmo conjunto de pacotes está disponível pelos repositórios
Debian:

```sh
sudo apt update
sudo apt install python3 python3-tk policykit-1 iw iproute2 aircrack-ng network-manager
```

O suporte ao modo monitor depende do adaptador Wi-Fi, driver e kernel.

## Instalação do pacote `.deb`

Baixe o pacote `twc.deb` na página de releases do projeto e instale-o com APT:

```sh
sudo apt install ./twc.deb
```

O APT instala também as dependências declaradas. Depois, abra **TWC — Total
Wireless Control** pelo menu de aplicativos. Para remover:

```sh
sudo apt remove twc
```

## Executar a partir do código

Em uma sessão gráfica, na raiz do projeto:

```sh
python3 twc.py
```

Se o programa ainda não estiver como root, ele solicita autenticação gráfica
uma vez pelo PolicyKit e reinicia a si mesmo com os privilégios necessários.
Não inicie o programa em um TTY sem sessão gráfica. Não use `sudo python3
twc.py`; deixe o PolicyKit cuidar da autenticação e do ambiente gráfico.

## Uso

1. Abra o TWC e autentique-se na janela do sistema.
2. Selecione a interface wireless e use **Atualizar** se necessário.
3. Use **Parar NetworkManager** ou **Parar processos Wi-Fi** somente quando
   necessário para a operação desejada.
4. Selecione **Descer interface**, altere para **Monitor** ou **Managed** e
   use **Subir interface** conforme necessário.
5. Ao terminar, retorne a interface para `managed` e, se necessário, use
   **Reiniciar NetworkManager**.
6. Para copiar comandos/resultados, selecione o texto no log ou clique com o
   botão direito e escolha **Copiar seleção**.

O teste rápido `iw` apenas consulta informações da interface; ele não testa
injeção de pacotes.

## Avisos de segurança e conectividade

- O TWC roda inteiramente como root depois de autenticado. Execute somente uma
  cópia do código em que confia.
- Descer a interface ou parar o NetworkManager pode derrubar sua conexão,
  inclusive uma sessão remota.
- `airmon-ng check kill` pode parar serviços e desconectar redes.
- O TWC não concede privilégios permanentes nem cria regras personalizadas do
  PolicyKit.

Leia também [SECURITY.md](SECURITY.md) antes de usar ou relatar problemas.

## Compilar o pacote Debian

Com `dpkg-deb` instalado, gere um pacote local:

```sh
./build-deb.sh
```

Por padrão, o resultado é `twc.deb` na raiz do projeto. Também é possível
escolher o caminho do arquivo:

```sh
./build-deb.sh dist/twc.deb
```

O pacote pode então ser instalado com `sudo apt install ./twc.deb`. Para
preparar uma nova versão, atualize `Version` em `debian/control` e adicione
uma entrada datada em `debian/changelog` antes de compilar.

## Desenvolvimento e contribuição

Leia [CONTRIBUTING.md](CONTRIBUTING.md) para orientações de alterações e
validação. O aplicativo usa somente a biblioteca padrão do Python e Tkinter;
não há dependências Python para instalar com `pip`.

## Contato e créditos

- **Autor/idealizador:** Benyvan (`@benyvan`)
- **E-mail:** [benyvan@gmail.com](mailto:benyvan@gmail.com)
- **Data do crédito:** 08/11/2026

Para citar este software, veja [CITATION.cff](CITATION.cff).

## Licença

Este projeto é distribuído sob a **GNU GPL versão 3 ou, a seu critério,
qualquer versão posterior**. Consulte o arquivo [LICENSE](LICENSE) para o
texto completo.
