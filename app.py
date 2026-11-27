"""Gerador de `Input.txt` para os programas da disciplina de MEF.

Interface Streamlit que recolhe os dados do modelo e escreve o ficheiro
`Input.txt` no mesmo formato dos ficheiros originais do professor.

Execução:
    streamlit run app.py

Notas de compatibilidade (obtidas ao ler os parsers):

* Os programas leem o ficheiro com `readline()` num número fixo de linhas e
  colunas. Por isso cada bloco abaixo repete os títulos, separadores e a ordem
  dos `Input.txt` originais.
* Linhas a mais no fim do ficheiro são inofensivas (o parser não as lê), daí o
  rodapé comentado com `#`.
* `Trelica (2).py` usa `area[2]` e `matriz_rotacao(coord, 2, inc)`; `Portico.py`
  usa `area[2]`, `inercia[2]` e `matriz_rotacao(coord, 4, inc)`. São prints de
  demonstração que impõem mínimos (3 secções, 3/5 elementos).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent
MARCA_CONFLITO = re.compile(r"^(<<<<<<< |>>>>>>> )", re.MULTILINE)

# ---------------------------------------------------------------------------
# Programas disponíveis
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Programa:
    rotulo: str
    pasta: str
    script: str
    gl: int  # graus de liberdade por nó
    coordenadas: bool
    cols_mat: tuple[str, ...]
    cols_sec: tuple[str, ...]
    min_elems: int
    min_secs: int
    nota: str
    saida: str


PROGRAMAS: dict[str, Programa] = {
    "Molas": Programa(
        rotulo="Molas",
        pasta="01_Mola",
        script="InvestMola.py",
        gl=1,
        coordenadas=False,
        cols_mat=("k",),
        cols_sec=(),
        min_elems=1,
        min_secs=0,
        nota="1 grau de liberdade por nó, sem coordenadas. O `const` do material é a rigidez k.",
        saida="imprime `desl` (1 valor por nó) e `forc`.",
    ),
    "Treliça plana": Programa(
        rotulo="Treliça plana",
        pasta="02_Trelica_Plana",
        script="Trelica (2).py",
        gl=2,
        coordenadas=True,
        cols_mat=("E",),
        cols_sec=("A",),
        min_elems=3,
        min_secs=3,
        nota="2 GL por nó (ux, uy), só esforço axial e cargas nodais.",
        saida="imprime `desl` (2 GL/nó), `reacoes` e `forca_norma` (positivo = tração).",
    ),
    "Pórtico plano": Programa(
        rotulo="Pórtico plano",
        pasta="03_Portico_Plano",
        script="Portico.py",
        gl=3,
        coordenadas=True,
        cols_mat=("E",),
        cols_sec=("A", "I"),
        min_elems=5,
        min_secs=3,
        nota="3 GL por nó (ux, uy, rotação). O parser ignora as cargas distribuídas: só cargas nodais.",
        saida="imprime `desl` (3 GL/nó), `reacoes` e o `f_int_elem` de cada barra.",
    ),
    "MEF 2D": Programa(
        rotulo="MEF 2D",
        pasta="04_MEF_2D/2_quadrilatero_4_nos",
        script="MEFBidimensional (2).py",
        gl=2,
        coordenadas=True,
        cols_mat=("E", "nu"),
        cols_sec=("t",),
        min_elems=1,
        min_secs=1,
        nota="Quadrilátero 4 nós (Gauss) ou triângulo 3 nós. EPD = 0, EPT = 1.",
        saida="escreve `Output.ogl` (AcadView) e imprime `desl`.",
    ),
}

# ---------------------------------------------------------------------------
# Modelo de dados
# ---------------------------------------------------------------------------
@dataclass
class No:
    i: int
    x: float = 0.0
    y: float = 0.0
    fx: float = 0.0
    fy: float = 0.0
    mz: float = 0.0


@dataclass
class Elemento:
    i: int
    nos: tuple[int, ...]
    mat: int
    sec: int


@dataclass
class Material:
    i: int
    vals: tuple[float, ...]


@dataclass
class Secao:
    i: int
    vals: tuple[float, ...]


@dataclass
class Apoio:
    no: int
    dir: int
    tipo: int
    valor: float


@dataclass
class Modelo:
    nos: list[No]
    elementos: list[Elemento]
    materiais: list[Material]
    secoes: list[Secao]
    apoios: list[Apoio]
    tipo_elemento: int = 1
    n_pont_int_csi: int = 2
    n_pont_int_eta: int = 2
    n_pont_int: int = 0
    n_nos_elem: int = 4
    tipo_ep: int = 1


# ---------------------------------------------------------------------------
# Formatação (notação científica, como nos ficheiros originais)
# ---------------------------------------------------------------------------
SEP_34 = "=================================="
SEP_48 = "================================================"


def _f(valor: float) -> str:
    return f"{float(valor):.6E}"


def _l(*cols: object) -> str:
    return "\t" + "\t".join(str(c) for c in cols)


def _texto(linhas: list[str], programa: str) -> str:
    rodape = [
        "",
        f"# Gerado por app.py em {datetime.now():%d/%m/%Y %H:%M} - programa: {programa}",
        "# Unidades: mantenha um sistema coerente (ex.: kN, m, kN/m2).",
    ]
    return "\n".join([*linhas, *rodape]) + "\n"


def _secoes_com_padding(secoes: list[Secao], minimo: int) -> list[Secao]:
    """Completa as secções até `minimo`, repetindo a última (ver `area[2]`)."""
    saida = list(secoes)
    while len(saida) < minimo:
        saida.append(Secao(i=len(saida) + 1, vals=saida[-1].vals))
    return saida


def _dados_gerais(nnos: int, nelems: int) -> list[str]:
    return [
        "===== DADOS GERAIS ==",
        "\tnnos\tnelems\t ",
        "=====================",
        _l(nnos, nelems),
        "=====================",
        "",
    ]


def _cargas(m: Modelo, gl: int) -> list[tuple[int, int, float]]:
    cargas: list[tuple[int, int, float]] = []
    for no in m.nos:
        if abs(no.fx) > 0:
            cargas.append((no.i, 1, no.fx))
        if gl >= 2 and abs(no.fy) > 0:
            cargas.append((no.i, 2, no.fy))
        if gl >= 3 and abs(no.mz) > 0:
            cargas.append((no.i, 3, no.mz))
    return cargas


def _bloco_carregamentos(cargas: list[tuple[int, int, float]]) -> list[str]:
    linhas = [
        "==== CARREGAMENTOS ===============",
        "\tncar",
        "==================================",
        _l(len(cargas)),
        "==================================",
        "\tno\t\tdir\t\tval",
        "==================================",
    ]
    linhas += [_l(no, direcao, _f(valor)) for no, direcao, valor in cargas]
    linhas += ["==================================", ""]
    return linhas


def _bloco_contorno(apoios: list[Apoio], *, titulo: str, com_valor: bool, separador: str) -> list[str]:
    linhas = [
        titulo,
        "\tn_cond_cont",
        separador,
        _l(len(apoios)),
        separador,
        "\tno\t\tdir\t\t\ttipo\t\t\tvalor" if com_valor else "\tno\t\tdir\t\ttipo",
    ]
    if com_valor:
        linhas.append("===================(1)rig= (2)mola==============")
    for ap in apoios:
        campos: list[object] = [ap.no, ap.dir, ap.tipo]
        if com_valor:
            campos.append(_f(ap.valor))
        linhas.append(_l(*campos))
    linhas.append(separador)
    return linhas

# ---------------------------------------------------------------------------
# Molas (01_Mola/InvestMola.py)
# ---------------------------------------------------------------------------
def gerar_molas(m: Modelo) -> str:
    linhas = _dados_gerais(len(m.nos), len(m.elementos))

    linhas += [
        "===== MATERIAIS ==========",
        "\tnmats",
        "==========================",
        _l(len(m.materiais)),
        "==========================",
        "\tmat\t\tconst",
        "==========================",
    ]
    linhas += [_l(mat.i, _f(mat.vals[0])) for mat in m.materiais]
    linhas += ["==========================", ""]

    linhas += [
        "==== ELEMENTOS ===================",
        "\telem\tno1\t\tno2\t\tmat",
        "==================================",
    ]
    linhas += [_l(e.i, e.nos[0], e.nos[1], e.mat) for e in m.elementos]
    linhas += ["==================================", ""]

    linhas += _bloco_carregamentos([(no.i, 1, no.fx) for no in m.nos if abs(no.fx) > 0])
    linhas += _bloco_contorno(
        m.apoios,
        titulo="=== CONDIÇÕES DE CONOTORNO =======",
        com_valor=False,
        separador=SEP_34,
    )
    return _texto(linhas, "01_Mola/InvestMola.py")


# ---------------------------------------------------------------------------
# Treliça plana (02_Trelica_Plana/Trelica (2).py)
# ---------------------------------------------------------------------------
def gerar_trelica(m: Modelo) -> str:
    secoes = _secoes_com_padding(m.secoes, 3)
    linhas = _dados_gerais(len(m.nos), len(m.elementos))

    linhas += [
        "===== MATERIAIS ==========",
        "\tnmats",
        "==========================",
        _l(len(m.materiais)),
        "==========================",
        "\tmat\t\tconst",
        "==========================",
    ]
    linhas += [_l(mat.i, _f(mat.vals[0])) for mat in m.materiais]
    linhas += ["==========================", ""]

    linhas += [
        "== SECOES TRANSVERSAIS ===",
        "\tnsect",
        "==========================",
        _l(len(secoes)),
        "==========================",
        "\tsecao\t\tarea",
        "==========================",
    ]
    linhas += [_l(sec.i, _f(sec.vals[0])) for sec in secoes]
    linhas += ["==========================", ""]

    linhas += [
        "==== COORDENADAS =============================",
        "\tno\tcoord_x\t\tcoord_y",
        "==============================================",
    ]
    linhas += [_l(no.i, _f(no.x), _f(no.y)) for no in m.nos]
    linhas += ["==============================================", ""]

    linhas += [
        "==== ELEMENTOS ===============================",
        "\telem\tno1\t\tno2\t\tmaterial\tsecao",
        "==============================================",
    ]
    linhas += [_l(e.i, e.nos[0], e.nos[1], e.mat, e.sec) for e in m.elementos]
    linhas += ["===============================================", ""]

    linhas += _bloco_carregamentos(_cargas(m, gl=2))
    linhas += _bloco_contorno(
        m.apoios,
        titulo="=== CONDIÇÕES DE CONOTORNO =======",
        com_valor=True,
        separador=SEP_48,
    )
    return _texto(linhas, "02_Trelica_Plana/Trelica (2).py")

# ---------------------------------------------------------------------------
# Pórtico plano (03_Portico_Plano/Portico.py)
# ---------------------------------------------------------------------------
def gerar_portico(m: Modelo) -> str:
    secoes = _secoes_com_padding(m.secoes, 3)
    linhas = _dados_gerais(len(m.nos), len(m.elementos))

    linhas += [
        "===== MATERIAIS ==========",
        "\tnmats",
        "==========================",
        _l(len(m.materiais)),
        "==========================",
        "\tmat\t\tconst",
        "==========================",
    ]
    linhas += [_l(mat.i, _f(mat.vals[0])) for mat in m.materiais]
    linhas += ["==========================", ""]

    linhas += [
        "== SECOES TRANSVERSAIS =========",
        "\tnsect",
        "=====================================",
        _l(len(secoes)),
        "=====================================",
        "\tsecao\t\tarea\tinercia",
        "=====================================",
    ]
    linhas += [_l(sec.i, _f(sec.vals[0]), _f(sec.vals[1])) for sec in secoes]
    linhas += ["=====================================", ""]

    linhas += [
        "==== COORDENADAS =============================",
        "\tno\tcoord_x\t\tcoord_y",
        "==============================================",
    ]
    linhas += [_l(no.i, _f(no.x), _f(no.y)) for no in m.nos]
    linhas += ["==============================================", ""]

    # 10 colunas como no original; as 5 últimas (carga distribuída) são lidas
    # mas ignoradas por esta versão do programa, que só usa lin[0]..lin[4].
    linhas += [
        "==== ELEMENTOS =======================================================================================================",
        "\telem\tno1\t\tno2\t\tmaterial\tsecao\ttipo_car_distr\t\t\t\tCarga_horizontal\tCarga_vertical",
        "============================================== (local = 1) = (global = 2)  == (qx1) ==\t(qx2) ==== (qy1) ==\t(qy2) ====",
    ]
    for e in m.elementos:
        linhas.append(_l(e.i, e.nos[0], e.nos[1], e.mat, e.sec, 1, _f(0), _f(0), _f(0), _f(0)))
    linhas += [
        "======================================================================================================================",
        "",
    ]

    linhas += _bloco_carregamentos(_cargas(m, gl=3))
    linhas += _bloco_contorno(
        m.apoios,
        titulo="=== CONDIÇÕES DE CONTORNO =====================",
        com_valor=True,
        separador=SEP_48,
    )
    return _texto(linhas, "03_Portico_Plano/Portico.py")

# ---------------------------------------------------------------------------
# MEF 2D (04_MEF_2D/2_quadrilatero_4_nos/MEFBidimensional (2).py)
# ---------------------------------------------------------------------------
def gerar_mef2d(m: Modelo) -> str:
    linhas = [
        "============================================================",
        "\t\t\t\ttipo de elemento",
        "=== Quadrilateral (1) == Triangular(2) =====================",
        _l(m.tipo_elemento),
        "============================================================",
        "",
        "==== Número de pontos de integração ========================",
        "tipo de elemento:  \t\t\tcsi\t\t\t\teta",
        "\tQuadrilateral(Gauss):  n_pont_int_csi\tn_pont_int_eta",
        "\tTriangular(Hammer):\t   n_pont_int\t",
        "-----------------------------------------------------------",
        "\tQuadrilateral",
        "==== n_pont_int_csi === n_pont_int_eta ====================",
    ]
    # O parser só lê os pontos de integração do tipo de elemento escolhido,
    # pelo que a linha de dados tem de estar na secção certa.
    if m.tipo_elemento == 1:
        linhas.append(_l(m.n_pont_int_csi, m.n_pont_int_eta))
    linhas += [
        "===========================================================",
        "\tTriangular",
        "==== n_pont_int ===========================================",
    ]
    if m.tipo_elemento == 2:
        linhas.append(_l(m.n_pont_int))
    linhas += [
        "===========================================================",
        "",
        "===== DADOS GERAIS =========================================",
        "\tnnos\tnelems\tn_nos_elem\t\t\ttipo_EP ",
        "================================ (EPD = 0) == (EPT = 1)=====",
        _l(len(m.nos), len(m.elementos), m.n_nos_elem, m.tipo_ep),
        "============================================================",
        "",
        "===== MATERIAIS ================",
        "\tnmats",
        "================================",
        _l(len(m.materiais)),
        "================================",
        "\tmat\t\tyoung\t\tpoisson",
        "================================",
    ]
    linhas += [_l(mat.i, _f(mat.vals[0]), _f(mat.vals[1])) for mat in m.materiais]
    linhas += ["================================", ""]

    linhas += [
        "== SECOES TRANSVERSAIS =========",
        "\tnsect",
        "=====================================",
        _l(len(m.secoes)),
        "=====================================",
        "\tsecao\t\tespessura\t",
        "=====================================",
    ]
    linhas += [_l(sec.i, _f(sec.vals[0])) for sec in m.secoes]
    linhas += ["=====================================", ""]

    linhas += [
        "==== COORDENADAS =============================",
        "\tno\tcoord_x\t\tcoord_y",
        "==============================================",
    ]
    linhas += [_l(no.i, _f(no.x), _f(no.y)) for no in m.nos]
    linhas += ["==============================================", ""]

    linhas += [
        "==== ELEMENTOS ====================================================",
        "\telem\tno1\t...\tn_nos_elem\t\tmaterial\tsecao_transversal",
        "===================================================================",
    ]
    linhas += [_l(e.i, *e.nos, e.mat, e.sec) for e in m.elementos]
    linhas += ["===================================================================", ""]

    linhas += _bloco_carregamentos(_cargas(m, gl=2))
    linhas += _bloco_contorno(
        m.apoios,
        titulo="=== CONDIÇÕES DE CONTORNO =====================",
        com_valor=True,
        separador=SEP_48,
    )
    return _texto(linhas, "04_MEF_2D/2_quadrilatero_4_nos/MEFBidimensional (2).py")


GERADORES: dict[str, Callable[[Modelo], str]] = {
    "Molas": gerar_molas,
    "Treliça plana": gerar_trelica,
    "Pórtico plano": gerar_portico,
    "MEF 2D": gerar_mef2d,
}

# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------
def _numeracao_ok(ids: list[int]) -> bool:
    """Os rótulos têm de ser exactamente 1..N (a ordem no ficheiro é livre)."""
    return sorted(ids) == list(range(1, len(ids) + 1))


def validar(m: Modelo, prog: Programa) -> tuple[list[str], list[str]]:
    erros: list[str] = []
    avisos: list[str] = []

    nnos = len(m.nos)
    if nnos < 2:
        erros.append("Defina pelo menos 2 nós.")

    ids_nos = [no.i for no in m.nos]
    if len(set(ids_nos)) != len(ids_nos):
        erros.append("Há números de nó repetidos.")
    nos_ok = _numeracao_ok(ids_nos)
    if not nos_ok:
        erros.append("Numere os nós de 1 a N sem saltos (o programa indexa arrays por `nó − 1`).")

    ids_el = [e.i for e in m.elementos]
    if not _numeracao_ok(ids_el):
        erros.append("Numere os elementos de 1 a M sem saltos.")
    if len(m.elementos) < prog.min_elems:
        erros.append(
            f"Este programa exige pelo menos {prog.min_elems} elementos: o código tem um print de "
            "demonstração que acede a `matriz_rotacao(coord, 2, inc)` (treliça) ou `(coord, 4, inc)` (pórtico)."
        )

    ids_mat = [mat.i for mat in m.materiais]
    if not ids_mat or not _numeracao_ok(ids_mat):
        erros.append("Numere os materiais de 1 a N sem saltos.")
    if prog.cols_sec:
        ids_sec = [sec.i for sec in m.secoes]
        if not ids_sec or not _numeracao_ok(ids_sec):
            erros.append("Numere as secções de 1 a N sem saltos.")
        if len(m.secoes) < prog.min_secs:
            avisos.append(
                "O programa usa `area[2]`/`inercia[2]` num print de demonstração: "
                "as secções em falta serão criadas iguais à última."
            )

    for e in m.elementos:
        for no in e.nos:
            if not 1 <= no <= nnos:
                erros.append(f"Elemento {e.i}: o nó {no} não existe.")
                break
        if len(set(e.nos)) != len(e.nos):
            erros.append(f"Elemento {e.i}: nós repetidos.")
        if not 1 <= e.mat <= len(m.materiais):
            erros.append(f"Elemento {e.i}: material {e.mat} não definido.")
        if prog.cols_sec and not 1 <= e.sec <= len(m.secoes):
            erros.append(f"Elemento {e.i}: secção {e.sec} não definida.")

    if prog.coordenadas and nos_ok:
        for e in m.elementos:
            if len(e.nos) != 2:
                continue
            no_a, no_b = m.nos[e.nos[0] - 1], m.nos[e.nos[1] - 1]
            if np.hypot(no_b.x - no_a.x, no_b.y - no_a.y) <= 1e-12:
                erros.append(
                    f"Elemento {e.i}: comprimento nulo (nós {e.nos[0]} e {e.nos[1]} coincidentes)."
                )

    if not m.apoios:
        erros.append("Defina pelo menos uma condição de contorno.")
    vistos: set[int] = set()
    for ap in m.apoios:
        if not 1 <= ap.no <= nnos:
            erros.append(f"Condição de contorno: o nó {ap.no} não existe.")
            continue
        if not 1 <= ap.dir <= prog.gl:
            erros.append(
                f"Condição de contorno (nó {ap.no}): direção {ap.dir} inválida (use 1 a {prog.gl})."
            )
        if ap.tipo != 1:
            erros.append(
                f"Condição de contorno (nó {ap.no}): tipo {ap.tipo} não está implementado "
                "— use 1 (apoio rígido)."
            )
        chave_gl = prog.gl * (ap.no - 1) + ap.dir
        if chave_gl in vistos:
            avisos.append(f"Condição de contorno repetida para o nó {ap.no}, direção {ap.dir}.")
        vistos.add(chave_gl)

    if prog.rotulo == "Treliça plana":
        livres = prog.gl * nnos - len(m.apoios)
        if len(m.elementos) < livres:
            avisos.append(
                f"Treliça com {len(m.elementos)} barras e {livres} GL livres: pode ser instável "
                "(condição necessária m ≥ 2n − r)."
            )

    if prog.rotulo == "MEF 2D":
        esperado = 4 if m.tipo_elemento == 1 else 3
        if m.n_nos_elem != esperado:
            erros.append("`n_nos_elem` tem de ser 4 (quadrilátero) ou 3 (triângulo).")
        for e in m.elementos:
            if len(e.nos) != m.n_nos_elem:
                erros.append(f"Elemento {e.i}: {len(e.nos)} nós, mas `n_nos_elem` = {m.n_nos_elem}.")
                break
        if m.tipo_elemento == 1:
            if m.n_pont_int_csi not in (1, 2, 3) or m.n_pont_int_eta not in (1, 2, 3):
                erros.append("A quadratura de Gauss implementada aceita 1, 2 ou 3 pontos por direção.")
            if nos_ok:
                avisos += _avisos_jacobiano(m)
        else:
            avisos.append(
                "A quadratura de Hammer do triângulo está por implementar nesta versão: "
                "`pontos_integracao` não devolve valores para tipo 2, logo a execução deve falhar."
            )

    return erros, avisos


def _avisos_jacobiano(m: Modelo) -> list[str]:
    """Verifica a ordem dos nós do quadrilátero pelo determinante do Jacobiano."""
    gauss = 1.0 / np.sqrt(3.0)
    pontos = [(-gauss, -gauss), (gauss, -gauss), (-gauss, gauss), (gauss, gauss)]
    avisos: list[str] = []
    for e in m.elementos:
        if len(e.nos) != 4:
            continue
        xy = np.array([[m.nos[no - 1].x, m.nos[no - 1].y] for no in e.nos], dtype=float)
        for csi, eta in pontos:
            dN = np.array(
                [
                    [-(1 - eta), -(1 - csi)],
                    [(1 - eta), -(1 + csi)],
                    [-(1 + eta), (1 - csi)],
                    [(1 + eta), (1 + csi)],
                ],
                dtype=float,
            ) / 4.0
            if np.linalg.det(dN.T @ xy) <= 0.0:
                avisos.append(
                    f"Elemento {e.i}: Jacobiano não positivo — confirme a ordem dos nós "
                    "(xmin,ymin), (xmax,ymin), (xmin,ymax), (xmax,ymax)."
                )
                break
    return avisos

# ---------------------------------------------------------------------------
# Modelos de exemplo (os do professor, quando existem)
# ---------------------------------------------------------------------------
def _exemplo(prog: Programa) -> dict[str, pd.DataFrame]:
    if prog.rotulo == "Molas":
        nos = pd.DataFrame({"No": [1, 2, 3, 4, 5], "F": [0.0, 400.0, 300.0, 500.0, 0.0]})
        elems = pd.DataFrame(
            {
                "Elem": [1, 2, 3, 4, 5, 6],
                "No1": [1, 2, 2, 2, 3, 4],
                "No2": [2, 3, 3, 4, 4, 5],
                "Mat": [1, 2, 3, 4, 5, 6],
            }
        )
        mats = pd.DataFrame(
            {"Mat": [1, 2, 3, 4, 5, 6], "k": [200.0, 100.0, 150.0, 300.0, 400.0, 500.0]}
        )
        secs = pd.DataFrame({"Sec": pd.Series(dtype="int64"), "A": pd.Series(dtype="float64")})
        cc = pd.DataFrame({"No": [1, 5], "Dir": [1, 1], "Tipo": [1, 1]})

    elif prog.rotulo == "Treliça plana":
        nos = pd.DataFrame(
            {
                "No": [1, 2, 3, 4],
                "x": [0.0, 600.0, 600.0, 0.0],
                "y": [0.0, 0.0, 800.0, 800.0],
                "Fx": [0.0, 0.0, 1000.0, 0.0],
                "Fy": [0.0, 0.0, 500.0, 0.0],
            }
        )
        elems = pd.DataFrame(
            {
                "Elem": [1, 2, 3, 4, 6, 5],
                "No1": [1, 2, 3, 4, 4, 1],
                "No2": [2, 3, 4, 1, 2, 3],
                "Mat": [1, 1, 1, 1, 1, 1],
                "Sec": [3, 2, 3, 2, 1, 1],
            }
        )
        mats = pd.DataFrame({"Mat": [1], "E": [2.1e4]})
        secs = pd.DataFrame({"Sec": [1, 2, 3], "A": [180.0, 240.0, 300.0]})
        cc = pd.DataFrame(
            {
                "No": [1, 1, 2, 2],
                "Dir": [1, 2, 1, 2],
                "Tipo": [1, 1, 1, 1],
                "Valor": [0.0, 0.0, 0.0, 0.0],
            }
        )

    elif prog.rotulo == "Pórtico plano":
        nos = pd.DataFrame(
            {
                "No": [1, 2, 3, 4, 5, 6, 7],
                "x": [0.0, 5.0e3, 5.0e3, 7.0e3, 9.0e3, 9.0e3, 9.0e3],
                "y": [0.0, 4.0e3, 0.0, 4.0e3, 4.0e3, 2.0e3, 0.0],
                "Fx": [0.0, 0.0, 0.0, 0.0, 0.0, -1.0e4, 0.0],
                "Fy": [0.0, 0.0, 0.0, -2.0e4, 0.0, 0.0, 0.0],
                "Mz": [0.0, 5.0e6, 0.0, 0.0, 0.0, 0.0, 0.0],
            }
        )
        elems = pd.DataFrame(
            {
                "Elem": [1, 2, 3, 4, 5, 6],
                "No1": [1, 3, 2, 4, 5, 6],
                "No2": [2, 2, 4, 5, 6, 7],
                "Mat": [1, 2, 2, 2, 2, 2],
                "Sec": [1, 3, 2, 2, 3, 3],
            }
        )
        mats = pd.DataFrame({"Mat": [1, 2], "E": [2.0e5, 2.0e4]})
        secs = pd.DataFrame(
            {"Sec": [1, 2, 3], "A": [1.08e3, 3.0e4, 9.0e4], "I": [1.051e6, 2.25e8, 6.75e8]}
        )
        cc = pd.DataFrame(
            {
                "No": [1, 1, 1, 3, 3, 7],
                "Dir": [1, 2, 3, 1, 2, 2],
                "Tipo": [1, 1, 1, 1, 1, 1],
                "Valor": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            }
        )

    else:  # MEF 2D
        nos = pd.DataFrame(
            {
                "No": [1, 2, 3, 4],
                "x": [0.0, 1.0, 0.0, 1.0],
                "y": [0.0, 0.0, 1.0, 1.0],
                "Fx": [0.0, 0.0, 0.0, 0.0],
                "Fy": [0.0, 0.0, 0.0, -1.0],
            }
        )
        elems = pd.DataFrame(
            {
                "Elem": [1],
                "No1": [1],
                "No2": [2],
                "No3": [3],
                "No4": [4],
                "Mat": [1],
                "Sec": [1],
            }
        )
        mats = pd.DataFrame({"Mat": [1], "E": [2.0e5], "nu": [0.30]})
        secs = pd.DataFrame({"Sec": [1], "t": [1.0]})
        cc = pd.DataFrame(
            {"No": [1, 1, 2], "Dir": [1, 2, 2], "Tipo": [1, 1, 1], "Valor": [0.0, 0.0, 0.0]}
        )

    return {"nos": nos, "elementos": elems, "materiais": mats, "secoes": secs, "cc": cc}

# ---------------------------------------------------------------------------
# Leitura das tabelas editadas
# ---------------------------------------------------------------------------
def _valor(linha: pd.Series, coluna: str, padrao: float = 0.0) -> float:
    bruto = linha.get(coluna, padrao)
    try:
        valor = float(bruto)
    except (TypeError, ValueError):
        return padrao
    return padrao if pd.isna(valor) else valor


def _inteiro(linha: pd.Series, coluna: str) -> int | None:
    bruto = linha.get(coluna)
    if bruto is None or pd.isna(bruto):
        return None
    try:
        return int(float(bruto))
    except (TypeError, ValueError):
        return None


def _modelo(
    prog: Programa,
    ed_nos: pd.DataFrame,
    ed_elems: pd.DataFrame,
    ed_mats: pd.DataFrame,
    ed_secs: pd.DataFrame,
    ed_cc: pd.DataFrame,
    extra: dict[str, int],
) -> Modelo:
    nos: list[No] = []
    for _, linha in ed_nos.iterrows():
        indice = _inteiro(linha, "No")
        if indice is None:
            continue
        carga = _valor(linha, "Fx") if "Fx" in ed_nos.columns else _valor(linha, "F")
        nos.append(
            No(
                i=indice,
                x=_valor(linha, "x"),
                y=_valor(linha, "y"),
                fx=carga,
                fy=_valor(linha, "Fy"),
                mz=_valor(linha, "Mz"),
            )
        )

    colunas_nos = [c for c in ed_elems.columns if re.fullmatch(r"No\d+", str(c))]
    esperado_nos = extra.get("n_nos_elem", 2)
    elementos: list[Elemento] = []
    for _, linha in ed_elems.iterrows():
        indice = _inteiro(linha, "Elem")
        if indice is None:
            continue
        conectividade = tuple(
            int(_valor(linha, coluna))
            for coluna in colunas_nos
            if _inteiro(linha, coluna) is not None
        )
        # linha incompleta: completa com 0 para a validação assinalar (e o
        # escritor não rebentar)
        if len(conectividade) < esperado_nos:
            conectividade += (0,) * (esperado_nos - len(conectividade))
        elementos.append(
            Elemento(
                i=indice,
                nos=conectividade,
                mat=_inteiro(linha, "Mat") or 0,
                sec=_inteiro(linha, "Sec") or 0,
            )
        )

    materiais = [
        Material(i=_inteiro(linha, "Mat") or 0, vals=tuple(_valor(linha, c) for c in prog.cols_mat))
        for _, linha in ed_mats.iterrows()
        if _inteiro(linha, "Mat") is not None
    ]
    secoes = [
        Secao(i=_inteiro(linha, "Sec") or 0, vals=tuple(_valor(linha, c) for c in prog.cols_sec))
        for _, linha in ed_secs.iterrows()
        if _inteiro(linha, "Sec") is not None
    ]
    apoios = [
        Apoio(
            no=_inteiro(linha, "No") or 0,
            dir=_inteiro(linha, "Dir") or 0,
            tipo=_inteiro(linha, "Tipo") or 0,
            valor=_valor(linha, "Valor"),
        )
        for _, linha in ed_cc.iterrows()
        if _inteiro(linha, "No") is not None
    ]

    # nós/materiais/secções em ordem de rótulo: as posições passam a coincidir
    # com `rótulo - 1`, que é como os programas indexam as arrays.
    nos.sort(key=lambda no: no.i)
    materiais.sort(key=lambda mat: mat.i)
    secoes.sort(key=lambda sec: sec.i)

    return Modelo(
        nos=nos,
        elementos=elementos,
        materiais=materiais,
        secoes=secoes,
        apoios=apoios,
        tipo_elemento=extra.get("tipo_elemento", 1),
        n_pont_int_csi=extra.get("n_pont_int_csi", 2),
        n_pont_int_eta=extra.get("n_pont_int_eta", 2),
        n_pont_int=extra.get("n_pont_int", 0),
        n_nos_elem=extra.get("n_nos_elem", 4),
        tipo_ep=extra.get("tipo_ep", 1),
    )


# ---------------------------------------------------------------------------
# Tabelas
# ---------------------------------------------------------------------------
def _cfg_num(
    rotulo: str,
    *,
    minimo: float | None = None,
    maximo: float | None = None,
    passo: float | None = None,
    formato: str = "%.6g",
) -> st.column_config.NumberColumn:
    return st.column_config.NumberColumn(
        rotulo, min_value=minimo, max_value=maximo, step=passo, format=formato, required=True
    )


def _editor(dados: pd.DataFrame, chave: str, config: dict, alt: str) -> pd.DataFrame:
    return st.data_editor(
        dados,
        key=chave,
        num_rows="dynamic",
        hide_index=True,
        column_config=config,
        alt=alt,
    )

# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------
def _avisos_repositorio() -> None:
    com_conflito: list[str] = []
    for prog in PROGRAMAS.values():
        for ficheiro in (RAIZ / prog.pasta / prog.script, RAIZ / prog.pasta / "Input.txt"):
            if not ficheiro.is_file():
                continue
            try:
                conteudo = ficheiro.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if MARCA_CONFLITO.search(conteudo):
                com_conflito.append(str(ficheiro.relative_to(RAIZ)))
    if com_conflito:
        st.warning(
            "Estes ficheiros ainda têm marcadores de conflito de merge (`<<<<<<<`) e não executam "
            "enquanto o merge não for resolvido: "
            + ", ".join(f"`{nome}`" for nome in com_conflito),
            title="Merge por resolver",
            icon=":material/warning:",
        )


def _ui_mef2d() -> dict[str, int]:
    st.subheader("Formulação")
    elemento = st.segmented_control(
        "Elemento",
        ["Quadrilátero (4 nós)", "Triângulo (3 nós)"],
        default="Quadrilátero (4 nós)",
        required=True,
        selection_mode="single",
        key="mef2d_elemento",
    )
    estado = st.segmented_control(
        "Estado plano",
        ["EPT (tensão)", "EPD (deformação)"],
        default="EPT (tensão)",
        required=True,
        selection_mode="single",
        key="mef2d_estado",
    )
    tipo_elemento = 1 if str(elemento).startswith("Quadrilátero") else 2
    tipo_ep = 1 if str(estado).startswith("EPT") else 0

    extra: dict[str, int] = {
        "tipo_elemento": tipo_elemento,
        "tipo_ep": tipo_ep,
        "n_nos_elem": 4 if tipo_elemento == 1 else 3,
    }
    if tipo_elemento == 1:
        col_csi, col_eta = st.columns(2)
        with col_csi:
            extra["n_pont_int_csi"] = int(
                st.number_input("Pontos de Gauss em ξ", min_value=1, max_value=3, value=2, step=1)
            )
        with col_eta:
            extra["n_pont_int_eta"] = int(
                st.number_input("Pontos de Gauss em η", min_value=1, max_value=3, value=2, step=1)
            )
        st.caption(
            "Ordem dos nós do quadrilátero, como no Input original: "
            "(xmin, ymin), (xmax, ymin), (xmin, ymax), (xmax, ymax)."
        )
    else:
        extra["n_pont_int"] = int(
            st.number_input("Pontos de integração (Hammer)", min_value=1, max_value=3, value=1, step=1)
        )
    return extra


def ui_modelo(prog: Programa) -> Modelo:
    extra: dict[str, int] = {}
    if prog.rotulo == "MEF 2D":
        extra = _ui_mef2d()

    padrao = _exemplo(prog)
    chave = prog.rotulo if prog.rotulo != "MEF 2D" else f"{prog.rotulo}_{extra['tipo_elemento']}"
    n_nos_elem = extra.get("n_nos_elem", 2)

    st.subheader("Nós e cargas nodais")
    if prog.gl == 1:
        config_nos = {"No": _cfg_num("Nó", minimo=1, passo=1, formato="%d"), "F": _cfg_num("Força F")}
        st.caption("Sistema de molas: 1 grau de liberdade por nó, sem coordenadas.")
    else:
        config_nos: dict = {
            "No": _cfg_num("Nó", minimo=1, passo=1, formato="%d"),
            "x": _cfg_num("x"),
            "y": _cfg_num("y"),
            "Fx": _cfg_num("Fx"),
            "Fy": _cfg_num("Fy"),
        }
        if prog.gl == 3:
            config_nos["Mz"] = _cfg_num("Mz (momento)")
    ed_nos = _editor(
        padrao["nos"], f"nos_{chave}", config_nos, "Tabela de nós, coordenadas e cargas nodais"
    )

    st.subheader("Elementos")
    colunas_el = ["Elem"] + [f"No{k}" for k in range(1, n_nos_elem + 1)] + ["Mat"]
    if prog.cols_sec:
        colunas_el.append("Sec")
    config_el: dict = {
        "Elem": _cfg_num("Elemento", minimo=1, passo=1, formato="%d"),
        "Mat": _cfg_num("Material", minimo=1, passo=1, formato="%d"),
    }
    if prog.cols_sec:
        config_el["Sec"] = _cfg_num("Secção", minimo=1, passo=1, formato="%d")
    for k in range(1, n_nos_elem + 1):
        config_el[f"No{k}"] = _cfg_num(f"Nó {k}", minimo=1, passo=1, formato="%d")
    ed_elems = _editor(
        padrao["elementos"][colunas_el], f"elem_{chave}", config_el, "Tabela de conectividades"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Materiais")
        config_mat: dict = {"Mat": _cfg_num("Material", minimo=1, passo=1, formato="%d")}
        for coluna in prog.cols_mat:
            config_mat[coluna] = _cfg_num(coluna)
        ed_mats = _editor(padrao["materiais"], f"mat_{chave}", config_mat, "Tabela de materiais")
    with col_b:
        st.subheader("Secções transversais")
        if prog.cols_sec:
            config_sec: dict = {"Sec": _cfg_num("Secção", minimo=1, passo=1, formato="%d")}
            for coluna in prog.cols_sec:
                config_sec[coluna] = _cfg_num(coluna)
            ed_secs = _editor(padrao["secoes"], f"sec_{chave}", config_sec, "Tabela de secções")
        else:
            st.caption("Este programa não usa secções transversais.")
            ed_secs = padrao["secoes"]

    st.subheader("Condições de contorno")
    config_cc: dict = {
        "No": _cfg_num("Nó", minimo=1, passo=1, formato="%d"),
        "Dir": _cfg_num("Direção", minimo=1, maximo=prog.gl, passo=1, formato="%d"),
        "Tipo": _cfg_num("Tipo", minimo=1, maximo=2, passo=1, formato="%d"),
    }
    if prog.gl > 1:
        config_cc["Valor"] = _cfg_num("Valor prescrito")
    ed_cc = _editor(padrao["cc"], f"cc_{chave}", config_cc, "Tabela de condições de contorno")

    direcoes = {1: "x", 2: "y", 3: "rotação"}
    st.caption(
        "Direções: "
        + ", ".join(f"{d} = {direcoes[d]}" for d in range(1, prog.gl + 1))
        + ". Tipo 1 = apoio rígido (o tipo 2, mola, não está implementado)."
    )

    return _modelo(prog, ed_nos, ed_elems, ed_mats, ed_secs, ed_cc, extra)

def main() -> None:
    st.set_page_config(page_title="Gerador de Input.txt", layout="centered")

    st.title("Gerador de `Input.txt`")
    st.caption(
        "Recolhe os dados do modelo e escreve o `Input.txt` no formato de cada programa. "
        "A pré-visualização já é o ficheiro final."
    )
    _avisos_repositorio()

    linha_topo_a, linha_topo_b = st.columns([3, 1], vertical_alignment="bottom")
    with linha_topo_a:
        programa = st.segmented_control(
            "Programa de destino",
            options=list(PROGRAMAS),
            default="Treliça plana",
            required=True,
            selection_mode="single",
            key="programa",
            help="Cada programa lê blocos e colunas diferentes no Input.txt.",
        )
    with linha_topo_b:
        if st.button(
            "Repor exemplo", icon=":material/restart_alt:", type="tertiary", width="stretch"
        ):
            for chave in [k for k in st.session_state if re.match(r"^(nos|elem|mat|sec|cc)_", str(k))]:
                del st.session_state[chave]
            st.rerun()

    if programa is None:
        st.stop()

    prog = PROGRAMAS[programa]
    st.caption(f"Pasta `{prog.pasta}` · script `{prog.script}` · {prog.nota}")

    modelo = ui_modelo(prog)
    erros, avisos = validar(modelo, prog)
    texto = GERADORES[programa](modelo)

    st.subheader("Pré-visualização do `Input.txt`")
    st.caption(
        f"{len(modelo.nos)} nós · {len(modelo.elementos)} elementos · "
        f"{len(_cargas(modelo, prog.gl))} cargas nodais · {len(modelo.apoios)} condições de contorno · "
        f"{len(texto.splitlines())} linhas"
    )
    st.code(texto, language="text", line_numbers=True)

    for mensagem in avisos:
        st.warning(mensagem, icon=":material/warning:")
    for mensagem in erros:
        st.error(mensagem, icon=":material/error:")

    st.subheader("Gerar o ficheiro")
    modo = st.radio(
        "Destino",
        [
            "Pasta do programa (substitui o `Input.txt`)",
            "Pasta `Generated/` (não altera os ficheiros do professor)",
        ],
        index=0,
        key=f"destino_{programa}",
    )
    if modo.startswith("Pasta do programa"):
        alvo = RAIZ / prog.pasta / "Input.txt"
    else:
        alvo = RAIZ / "Generated" / prog.pasta / "Input.txt"
    st.caption(f"Ficheiro: `{alvo.relative_to(RAIZ)}`")

    col_gerar, col_descarregar = st.columns(2, vertical_alignment="bottom")
    with col_gerar:
        gerar = st.button(
            "Gerar Input.txt",
            type="primary",
            icon=":material/save:",
            width="stretch",
            disabled=bool(erros),
        )
    with col_descarregar:
        st.download_button(
            "Descarregar",
            data=texto.encode("utf-8"),
            file_name="Input.txt",
            mime="text/plain",
            icon=":material/download:",
            width="stretch",
            disabled=bool(erros),
        )

    if gerar:
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(texto, encoding="utf-8", newline="\n")
        st.success(f"`Input.txt` gravado em `{alvo}`.", icon=":material/check_circle:")
        st.code(f'cd "{alvo.parent}"\npython "{prog.script}"', language="powershell")
        st.caption(f"O programa {prog.saida}")


if __name__ == "__main__":
    main()
