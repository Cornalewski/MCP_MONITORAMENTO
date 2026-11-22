import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain.mcp import MCPAdapter
from langchain_openai import ChatOpenAI


MCP_SERVER_URL = "http://localhost:9000/mcp"


async def create_mcp_agent():
    adapter = MCPAdapter(MCP_SERVER_URL)
    tools = await adapter.list_tools()

    model = ChatOpenAI(
        model="gpt-5.4-mini",
        temperature=0,
    )

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "Você é um assistente que consulta informações do servidor "
            "usando as ferramentas MCP disponíveis. "
            "Use as ferramentas para obter os dados solicitados. "
            "Para pedidos fora desse escopo, explique que você atende "
            "somente consultas cobertas pelas ferramentas disponíveis."
        ),
    )


async def start():
    agent = await create_mcp_agent()
    messages = []

    print("Type a message. Use 'quit' to stop.")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() == "quit":
            break

        if not user_input:
            continue

        messages.append(HumanMessage(content=user_input))
        result = await agent.ainvoke({"messages": messages})
        messages = result["messages"]

        print(messages[-1].content)


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
