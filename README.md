# Informações do sistema via MCP

Servidor MCP que consulta informações da máquina onde está executando e cliente de terminal que usa um agente LangChain para acessar essas ferramentas.

O servidor atende em `http://127.0.0.1:9000/mcp`. O cliente está configurado para `http://localhost:9000/mcp`.

## Requisitos

- Python 3.10 ou superior. Versões das dependências selecionadas a partir do ambiente Python 3.14.4 deste projeto.
- Acesso à internet para instalar as dependências e usar o modelo.
- Uma chave da API da OpenAI com acesso ao modelo configurado no cliente: `gpt-5.4-mini`.

O servidor de informações do sistema funciona sem chave da OpenAI. A chave é utilizada pelo cliente para acessar o modelo.

## Estrutura

```text
MCP_MONITORAMENTO/
├── README.md
├── requirements.txt                    # Instala cliente e servidor
├── MCP_SERVER/
│   └── mcp_server/
│       ├── __init__.py
│       ├── Main.py                     # Servidor e ferramentas MCP
│       ├── Models.py                   # Modelos Pydantic das respostas
│       └── requirements.txt            # Dependências do servidor
│
└── MCP_CLIENT/
    └── mcp_client/
        ├── main.py                     # Agente e conversa pelo terminal
        └── requirements.txt            # Dependências do cliente
```

## 1. Instalar as dependências

Abra um terminal na raiz de `MCP_MONITORAMENTO`, onde estão este README e o `requirements.txt`. Escolha os comandos do seu sistema operacional.

### Linux e macOS — Bash ou Zsh

```bash
python3 --version
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pip check
```

### Windows — PowerShell

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

## 2. Iniciar o servidor — terminal 1

Abra um terminal na raiz do projeto e escolha os comandos do seu sistema:

### Linux e macOS — Bash ou Zsh

```bash
cd MCP_SERVER
../.venv/bin/python -m mcp_server.Main
```

### Windows — PowerShell

```powershell
cd MCP_SERVER
..\.venv\Scripts\python.exe -m mcp_server.Main
```

Mantenha esse terminal aberto. O servidor escuta em `127.0.0.1:9000`, acessível pela própria máquina.

Execute como módulo, respeitando a letra maiúscula de `Main`. Isso permite que o import relativo `from .Models import ...` funcione.

## 3. Iniciar o cliente — terminal 2

Abra outro terminal na raiz do projeto, configure a chave e inicie a conversa:

### Linux e macOS — Bash ou Zsh

```bash
cd MCP_CLIENT
export OPENAI_API_KEY='SUBSTITUA_PELA_SUA_CHAVE'
../.venv/bin/python -m mcp_client.main
```

### Windows — PowerShell

```powershell
cd MCP_CLIENT
$env:OPENAI_API_KEY = 'SUBSTITUA_PELA_SUA_CHAVE'
..\.venv\Scripts\python.exe -m mcp_client.main
```

A variável vale para esse terminal e seus processos. O código atual não carrega um arquivo `.env` automaticamente.

Quando aparecer `>`, faça uma pergunta, por exemplo:

```text
Qual é o processador deste servidor?
Quanto espaço está disponível na raiz?
Quanta memória RAM está disponível?
Qual é o uso médio da CPU e o uso por processador lógico?
Quantos processos existem neste momento?
Qual é a versão do sistema operacional?
```

Digite `quit` para sair. Para encerrar o servidor, pressione `Ctrl+C` no terminal 1.

## Ferramentas disponíveis

| Ferramenta | Retorno |
| --- | --- |
| `get_cpu_details` | Nome, arquitetura e outras características do processador. |
| `availableRoot` | Caminho da raiz consultada e espaço disponível, em bytes. |
| `sizeRoot` | Caminho da raiz consultada e capacidade total, em bytes. |
| `kernelVersion` | Sistema operacional e seu release; no Linux, versão do kernel. |
| `availableRAM` | Memória RAM disponível, em bytes. |
| `tasks` | Quantidade de processos existentes, incluindo os que estão aguardando ou dormindo. |
| `cpuUsage` | Uso médio e por processador lógico, quantidade de CPUs lógicas e núcleos físicos e duração da amostra. |

`cpuUsage` mede uma janela de um segundo; cada consulta leva aproximadamente esse tempo. Os valores são porcentagens de utilização, sem histórico de vários minutos. `systemLoad` foi substituída por essa ferramenta.

No Linux e no macOS, a raiz consultada é `/`. No Windows, é a raiz da unidade do diretório atual, como `C:\`. Os números se referem ao sistema de arquivos dessa raiz, não à soma de todos os discos da máquina. No macOS, `kernelVersion` identifica o sistema como `Darwin` e retorna o release do kernel Darwin, que é diferente da versão comercial do macOS.

As respostas são modelos Pydantic. As descrições dos campos ficam no esquema de saída das ferramentas. Os valores indisponíveis de campos opcionais são retornados como `null`.

## Conferir a conexão sem chamar o modelo

Com o servidor aberto, execute a partir da raiz do projeto:

### Linux e macOS — Bash ou Zsh

```bash
./.venv/bin/python -c "import asyncio; from langchain.mcp import MCPAdapter; tools = asyncio.run(MCPAdapter('http://localhost:9000/mcp').list_tools()); print([tool.name for tool in tools])"
```

### Windows — PowerShell

```powershell
.\.venv\Scripts\python.exe -c "import asyncio; from langchain.mcp import MCPAdapter; tools = asyncio.run(MCPAdapter('http://localhost:9000/mcp').list_tools()); print([tool.name for tool in tools])"
```

O comando deve listar as sete ferramentas da tabela. Ele não usa a chave da OpenAI nem faz chamadas ao modelo. A integração `langchain.mcp` pode emitir um aviso de que sua API está em beta.

## Problemas comuns

- **Import relativo sem pacote conhecido:** use `-m mcp_server.Main` a partir de `MCP_SERVER`; não execute `Main.py` diretamente.
- **Módulo não encontrado:** confirme que usa o Python de `.venv` na raiz e que instalou o requirements da raiz.
- **Erro ao importar `RequestContext`:** confirme que o cliente importa `MCPAdapter` de `langchain.mcp`. Recrie um ambiente virtual limpo seguindo a instalação, se estiver usando pacotes globais incompatíveis.
- **Falha de conexão:** inicie o servidor primeiro e confira a porta `9000`. Se alterar host ou porta no servidor, ajuste `MCP_SERVER_URL` no cliente.
- **Chave ausente ou inválida:** configure `OPENAI_API_KEY` no mesmo terminal onde executa o cliente.
- **Modelo indisponível para sua conta:** ajuste `model=` em `MCP_CLIENT/mcp_client/main.py` para um modelo com suporte a ferramentas disponível na sua conta.
