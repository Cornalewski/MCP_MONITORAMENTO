import asyncio
import cpuinfo as ci
from fastmcp import FastMCP
import psutil as ps
import platform
from pathlib import Path
import time
from typing import Annotated, Literal
from pydantic import Field


from .Models import (
    CPUUsage,
    RootAvailable,
    RootSize,
    KernelVersion,
    RAMAvailable,
    TaskCount,
    CPUInfo,
    SystemLoad,
    ProcessInfo
)

mcp = FastMCP(
    name="System Information about the current server",
    instructions="Provides information about the current server, including its hostname, IP address, and operating system and other hardware information.",
)

def get_root_path() -> str:
    return Path.cwd().anchor


@mcp.tool(name="availableRoot")
def available_root() -> RootAvailable:
    """Retorna o espaço disponível no sistema de arquivos raiz."""
    root = get_root_path()

    return RootAvailable(
        path=root,
        available_bytes=ps.disk_usage(root).free,
    )


@mcp.tool(name="sizeRoot")
def size_root() -> RootSize:
    """Retorna a capacidade total do sistema de arquivos raiz."""
    root = get_root_path()

    return RootSize(
        path=root,
        total_bytes=ps.disk_usage(root).total,
    )


@mcp.tool(name="kernelVersion")
def kernel_version() -> KernelVersion:
    """Retorna o sistema operacional e seu release; no Linux, versão do kernel."""
    return KernelVersion(
        system=platform.system(),
        release=platform.release(),
    )


@mcp.tool(name="availableRAM")
def available_ram() -> RAMAvailable:
    """Retorna a quantidade de memória RAM disponível."""
    return RAMAvailable(
        available_bytes=ps.virtual_memory().available,
    )


@mcp.tool(name="tasks")
def tasks() -> TaskCount:
    """Retorna a quantidade de processos existentes, sem contar threads à parte."""
    return TaskCount(
        process_count=len(ps.pids()),
    )


@mcp.tool(name="cpuUsage")
def cpu_usage() -> CPUUsage:
    """Mede o uso médio da CPU e por processador lógico durante 1 segundo."""
    per_cpu = ps.cpu_percent(interval=1.0, percpu=True)

    return CPUUsage(
        average_percent=round(sum(per_cpu) / len(per_cpu), 2),
        per_cpu_percent=per_cpu,
        logical_cpus=len(per_cpu),
        physical_cores=ps.cpu_count(logical=False),
        sample_seconds=1.0,
    )

@mcp.tool(name="cpuName")
def cpu_name() -> CPUInfo:
    """Retorna identificação e características do processador do servidor.

    Campos indisponíveis são retornados como null.
    """
    return CPUInfo(**ci.get_cpu_info())

@mcp.tool(name="systemLoad")
def system_load() -> SystemLoad:
    """Retorna a carga média em 1, 5 e 15 minutos. Os valores não são percentuais."""
    one, five, fifteen = ps.getloadavg()

    return SystemLoad(
        average_1m=one,
        average_5m=five,
        average_15m=fifteen,
    )

@mcp.tool(name="topProcesses")
def top_processes(
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=50,
            description="Quantidade máxima de processos retornados.",
        ),
    ] = 5,
    order: Literal["cpu", "memory"] = "cpu",
) -> list[ProcessInfo]:
    """Retorna os processos que mais usam CPU ou RAM.

    A utilização de CPU é medida durante aproximadamente 1 segundo.
    """
    tracked = []

    # Inicia a medição de todos os processos.
    for pid in ps.pids():
        try:
            process = ps.Process(pid)
            process.cpu_percent(interval=None)
            tracked.append(process)
        except (ps.NoSuchProcess, ps.AccessDenied):
            continue

    # Espera uma única vez para toda a coleta.
    time.sleep(1.0)

    results = []

    for process in tracked:
        try:
            results.append(
                ProcessInfo(
                    pid=process.pid,
                    name=process.name(),
                    cpu_percent=process.cpu_percent(interval=None),
                    memory_bytes=process.memory_info().rss,
                )
            )
        except (ps.NoSuchProcess, ps.AccessDenied):
            continue

    if order == "cpu":
        return sorted(
            results,
            key=lambda item: item.cpu_percent,
            reverse=True,
        )[:limit]

    return sorted(
        results,
        key=lambda item: item.memory_bytes,
        reverse=True,
    )[:limit]


async def run_server() -> None:
    """Run the MCP server asynchronously over HTTP."""
    await mcp.run_async(transport="http", host="127.0.0.1", port=9000)


def main() -> None:
    """Start the async MCP server from the package's console entry point."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()