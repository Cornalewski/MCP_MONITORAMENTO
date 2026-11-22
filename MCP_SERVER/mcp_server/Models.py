from pydantic import BaseModel, Field


class CPUInfo(BaseModel):
    brand_raw: str | None = Field(
        default=None,
        description="Nome comercial completo do processador.",
    )

    arch: str | None = Field(
        default=None,
        description="Arquitetura do processador, como X86_64 ou ARM_8.",
    )

    count: int | None = Field(
        default=None,
        description="Quantidade de processadores lógicos identificados.",
    )

    hz_advertised_friendly: str | None = Field(
        default=None,
        description="Frequência anunciada do processador, incluindo a unidade.",
    )

    l3_cache_size: int | None = Field(
        default=None,
        description="Tamanho do cache L3 em bytes.",
    )

    flags: list[str] | None = Field(
        default=None,
        description="Recursos e extensões de instruções identificados.",
    )
    
class RootAvailable(BaseModel):
    path: str = Field(description="Raiz do sistema de arquivos consultado.")
    available_bytes: int = Field(
        description="Espaço disponível no sistema de arquivos, em bytes."
    )


class RootSize(BaseModel):
    path: str = Field(description="Raiz do sistema de arquivos consultado.")
    total_bytes: int = Field(
        description="Capacidade total do sistema de arquivos, em bytes."
    )


class KernelVersion(BaseModel):
    system: str = Field(description="Sistema operacional, como Linux ou Windows.")
    release: str = Field(
        description="Release do sistema operacional; no Linux, versão do kernel."
    )


class RAMAvailable(BaseModel):
    available_bytes: int = Field(
        description="RAM disponível para aplicações sem recorrer à swap, em bytes."
    )


class TaskCount(BaseModel):
    process_count: int = Field(
        description=(
            "Quantidade de processos existentes no momento da consulta, "
            "incluindo processos que estão aguardando ou dormindo."
        )
    )


class CPUUsage(BaseModel):
    average_percent: float = Field(
        ge=0,
        le=100,
        description="Média de utilização dos processadores lógicos, em porcentagem.",
    )

    per_cpu_percent: list[float] = Field(
        description=(
            "Utilização de cada processador lógico, de 0 a 100%. "
            "A posição na lista indica seu índice, começando em zero."
        ),
    )

    logical_cpus: int = Field(
        description="Quantidade de processadores lógicos incluídos na medição.",
    )

    physical_cores: int | None = Field(
        default=None,
        description="Quantidade de núcleos físicos; null quando indisponível.",
    )

    sample_seconds: float = Field(
        description="Duração da amostra utilizada na medição, em segundos.",
    )