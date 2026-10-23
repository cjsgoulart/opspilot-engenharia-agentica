"""Testes OFFLINE da integração com Langfuse (Aula 4)."""

import sys
from contextlib import contextmanager
from types import ModuleType

from langchain_core.messages import AIMessage

from opspilot import observabilidade
from opspilot.config import LIMITE_RECURSAO
from opspilot.prompts import VERSAO_PROMPT


class AgenteFalso:
    def __init__(self):
        self.config = None

    def invoke(self, entrada, config):
        self.config = config
        return {"messages": [AIMessage(content="Diagnóstico pronto")]}


def test_invocar_sem_langfuse_preserva_execucao(monkeypatch):
    agente = AgenteFalso()
    monkeypatch.setattr(observabilidade, "cliente_langfuse", lambda: None)

    saida = observabilidade.invocar_com_trace(agente, "Investigue o incidente")

    assert saida == {
        "resposta": "Diagnóstico pronto",
        "estado": {"messages": [AIMessage(content="Diagnóstico pronto")]},
        "trace_id": None,
        "trace_url": None,
    }
    assert agente.config == {"recursion_limit": LIMITE_RECURSAO}


def test_invocar_com_trace_registra_contexto_e_resposta(monkeypatch):
    class SpanFalso:
        output = None

        def __enter__(self):
            return self

        def __exit__(self, tipo, valor, traceback):
            return False

        def update(self, *, output):
            self.output = output

    class ClienteFalso:
        def __init__(self):
            self.span = SpanFalso()
            self.observacao = None

        def start_as_current_observation(self, **kwargs):
            self.observacao = kwargs
            return self.span

        def get_current_trace_id(self):
            return "trace-123"

        def get_trace_url(self, *, trace_id):
            return f"https://langfuse.example/traces/{trace_id}"

    atributos = {}

    @contextmanager
    def propagar(**kwargs):
        atributos.update(kwargs)
        yield

    class HandlerFalso:
        pass

    modulo_langfuse = ModuleType("langfuse")
    modulo_langfuse.propagate_attributes = propagar
    modulo_langchain = ModuleType("langfuse.langchain")
    modulo_langchain.CallbackHandler = HandlerFalso
    monkeypatch.setitem(sys.modules, "langfuse", modulo_langfuse)
    monkeypatch.setitem(sys.modules, "langfuse.langchain", modulo_langchain)

    cliente = ClienteFalso()
    agente = AgenteFalso()
    monkeypatch.setattr(observabilidade, "cliente_langfuse", lambda: cliente)

    saida = observabilidade.invocar_com_trace(
        agente,
        "Investigue o incidente",
        nome="opspilot-fsm",
        session_id="sessao-1",
        user_id="plantao-1",
        tags=["aula4"],
    )

    assert cliente.observacao == {
        "as_type": "agent",
        "name": "opspilot-fsm",
        "input": {"pergunta": "Investigue o incidente"},
    }
    assert atributos == {
        "session_id": "sessao-1",
        "user_id": "plantao-1",
        "tags": ["aula4"],
        "version": VERSAO_PROMPT,
    }
    assert agente.config["recursion_limit"] == LIMITE_RECURSAO
    assert isinstance(agente.config["callbacks"][0], HandlerFalso)
    assert cliente.span.output == {"resposta": "Diagnóstico pronto"}
    assert saida["trace_id"] == "trace-123"
    assert saida["trace_url"] == "https://langfuse.example/traces/trace-123"


def test_registrar_nota_cria_score_no_trace(monkeypatch):
    class ClienteFalso:
        score = None

        def create_score(self, **kwargs):
            self.score = kwargs

    cliente = ClienteFalso()
    monkeypatch.setattr(observabilidade, "cliente_langfuse", lambda: cliente)

    observabilidade.registrar_nota("trace-123", "fundamentacao", 4, "Bem fundamentado")

    assert cliente.score == {
        "trace_id": "trace-123",
        "name": "fundamentacao",
        "value": 4.0,
        "comment": "Bem fundamentado",
    }
