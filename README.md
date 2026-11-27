# MEF — Método dos Elementos Finitos

Material da disciplina de Introdução ao Método dos Elementos Finitos (programação de
elementos estruturais em Python + teoria, listas e livro de referência).

Organização feita por **elemento estrutural** (do mais simples para o mais complexo),
com os programas de cada tópico agrupados e cada um com o seu próprio `Input.txt`
executável.

---

## Estrutura

```
MEF/
├── README.md                       ← este ficheiro
├── Teoria/                         ← PDFs de teoria (aulas)
├── Listas/                         ← listas de exercícios
├── Livro/                          ← bibliografia
│
├── 01_Mola/                        ← sistema de molas (1 GL por nó)
├── 02_Trelica_Plana/               ← treliça plana (2 GL por nó)
│   └── esqueleto/                  ← versão inicial (só leitura de dados)
├── 03_Portico_Plano/               ← pórtico plano (3 GL por nó)
└── 04_MEF_2D/                      ← elementos finitos 2D (EPD/EPT)
    ├── 1_constitutiva/             ← matriz constitutiva (aula)
    ├── 2_quadrilatero_4_nos/       ← programa completo (quadrilátero + triângulo)
    └── 3_historico/                ← versão intermédia incompleta (referência)
```

---

## Mapa: ficheiro → programa

| Pasta | Programa | Ficheiro de dados | Elemento / matéria | Estado |
|---|---|---|---|---|
| `01_Mola` | `InvestMola.py` | `Input.txt` | Molas (1 GL/nó) — montagem de rigidez, CC, resolução | Corre |
| `02_Trelica_Plana` | `Trelica (2).py` | `Input.txt` | Treliça plana (2 GL/nó) — **versão corrigida** | Corre |
| `02_Trelica_Plana` | `Trelica (1).py` | `Input.txt` | Treliça plana — 1ª versão (reações = `K·u`) | Corre (reações erradas) |
| `02_Trelica_Plana/esqueleto` | `Trelica.py` | `Input.txt` | Treliça — esqueleto: só leitura de dados + *prints* | Corre (sem cálculo) |
| `03_Portico_Plano` | `Portico.py` | `Input.txt` | Pórtico plano (3 GL/nó: axial + flexão) | Corre |
| `04_MEF_2D/1_constitutiva` | `MEFBidimensional.py` | `Input.txt` | Matriz constitutiva EPD/EPT (resto do código comentado) | Corre |
| `04_MEF_2D/2_quadrilatero_4_nos` | `MEFBidimensional (2).py` | `Input.txt` | Quadrilátero 4 nós (Gauss 2×2) + triângulo (Hammer) — **programa completo** | Corre |
| `04_MEF_2D/3_historico` | `MEFBidimensional (1).py` | — | Versão intermédia do programa 2D | **Não corre** (erros de sintaxe) |

Documentos:

| Pasta | Ficheiro |
|---|---|
| `Teoria` | `MEF.pdf` — introdução ao MEF |
| `Teoria` | `Programacao_Trelicas_Planas.pdf` — programação de treliças planas |
| `Teoria` | `Aula_11_MEF_Integracao_Numerica.pdf` — integração numérica (Gauss/Hammer) |
| `Listas` | `Lista_01_IMEF.pdf`, `Lista_02_IMEF.pdf`, `Lista_03_IMEF.pdf` |
| `Livro` | `(2013, Alves Filho) Elementos Finitos A base da tecnologia CAE.pdf` |

---

## Como executar

Todos os programas abrem o ficheiro **`"Input.txt"` por caminho relativo**, ou seja, no
diretório de trabalho atual. Por isso é obrigatório entrar primeiro na pasta do programa
(cada pasta tem o seu próprio `Input.txt`, já com os dados do modelo correspondente).

```powershell
cd "C:\Users\Kaichou\Downloads\MEF\02_Trelica_Plana"
python "Trelica (2).py"
```

Outros exemplos:

```powershell
cd "C:\Users\Kaichou\Downloads\MEF\01_Mola";                       python "InvestMola.py"
cd "C:\Users\Kaichou\Downloads\MEF\03_Portico_Plano";              python "Portico.py"
cd "C:\Users\Kaichou\Downloads\MEF\04_MEF_2D\2_quadrilatero_4_nos"; python "MEFBidimensional (2).py"
```

Requisitos: Python 3 + NumPy. Testado com Python 3.14.6 e NumPy 2.5.4.

O `MEFBidimensional (2).py` escreve o ficheiro de pós-processamento **`Output.ogl`**
(no diretório de trabalho), para visualização no programa AcadView.

---

## Formato dos ficheiros de entrada (`Input.txt`)

Os ficheiros seguem um padrão de blocos separados por linhas de `====`, lidos
sequencialmente com `readline()` na mesma ordem em que aparecem:

1. **DADOS GERAIS** — `nnos`, `nelems` (+ no programa 2D: `n_nos_elem`, `tipo_EP`)
2. **MATERIAIS** — `nmats` e depois `mat, const` (mola) ou `mat, young, poisson` (2D)
3. **SECOES TRANSVERSAIS** — `nsect` e depois `secao, area, inercia` (pórtico) ou
   `secao, espessura` (2D)
4. **COORDENADAS** — `no, coord_x, coord_y` (nos programas com geometria)
5. **ELEMENTOS** — `elem, no1, no2, material, secao` (barras) ou `elem, no1..no4, material, secao`
6. **CARREGAMENTOS** — `ncar` e depois `no, dir, val`
7. **CONDIÇÕES DE CONTORNO** — `n_cond_cont` e depois `no, dir, tipo, valor`

> ⚠️ **Não troque os `Input.txt` entre pastas.** Cada programa lê um número fixo de
> linhas e de colunas; um ficheiro com blocos a mais ou a menos faz o parser ler a
> linha errada (sem dar erro, apenas resultados absurdos).

Diferenças entre ficheiros de dados:

| Pasta | Nós / elementos | Materiais | Secções | Coordenadas | Extras |
|---|---|---|---|---|---|
| `01_Mola` | 5 / 6 | 6 (`const` = rigidez da mola) | — | — | — |
| `02_Trelica_Plana` | 4 / 6 | 3 (`const` = E·A) | 3 (`area`) | Sim | — |
| `02_Trelica_Plana/esqueleto` | 4 / 6 | 1 | 3 (`area`) | — | — |
| `03_Portico_Plano` | 7 / 6 | 2 (`const` = E) | 3 (`area`, `inercia`) | Sim | colunas de carga distribuída |
| `04_MEF_2D/1_constitutiva` | 12 / 5 | 1 (`young`, `poisson`) | 1 (`espessura`) | Sim | — |
| `04_MEF_2D/2_quadrilatero_4_nos` | 12 / 5 | 1 (`young`, `poisson`) | 1 (`espessura`) | Sim | `tipo de elemento` + `n_pont_int` |

---

## Notas e limitações (encontradas ao executar o código)

**`01_Mola/InvestMola.py`**
- Cada nó tem 1 único grau de liberdade (`ngl = 1 * nnos`).
- Aplicação de CC: só trata o tipo **1 (rigidez/apoio)**; o tipo **2 (mola)** referido no
  cabeçalho do `Input.txt` **não está implementado** (o `if` testa apenas `cc[ilin] == 1`).
- Usa `np.linalg.inv` e depois `np.linalg.solve` (o resultado é impresso duas vezes).

**`02_Trelica_Plana/Trelica.py` (esqueleto)**
- Só lê os dados e imprime `nnos`, `nelems`, `area`, `inc`, `material`, `secao`,
  `tipo_cc`, `valor_cc`. Toda a montagem da matriz de rigidez está comentada com `########`.

**`02_Trelica_Plana/Trelica (1).py` vs `Trelica (2).py`**
- `(1)`: `reacoes = np.dot(k_estr, desl)` — **não subtrai** o vetor de forças aplicadas,
  logo as reações incluem as cargas nodais (valores errados).
- `(2)`: `reacoes = np.dot(k_estr, desl) - f_estr` e o sinal da força normal foi corrigido
  (`forca_normal = -f_int_elem[0]`). **Use esta versão.**

**`03_Portico_Plano/Portico.py`**
- Lê os elementos com **apenas 5 colunas** (`elem, no1, no2, material, secao`), por isso
  as colunas de **carga distribuída** do `Input.txt` (`tipo_car_distr`, `qx1`, `qx2`,
  `qy1`, `qy2`) são **ignoradas** — o programa só considera cargas nodais.
- `reacoes = np.zeros((2*nnos))` é uma linha inútil (logo é reatribuída com `3*nnos`).
- `forca_interna()` devolve apenas o último elemento calculado (o `f_int_elem` é
  sobrescrito dentro do ciclo).
- O programa com cargas distribuídas (cargas nodais equivalentes) não está nesta pasta.

**`04_MEF_2D/1_constitutiva/MEFBidimensional.py`**
- Calcula e imprime apenas a **matriz constitutiva** (`matriz_const`) para EPD (`tipo_EP = 0`)
  ou EPT (`tipo_EP = 1`); o resto do código está dentro de `"""..."""`.
- Herda `ngl = 3 * nnos` do código de pórtico (o programa 2D completo usa `2 * nnos`).

**`04_MEF_2D/2_quadrilatero_4_nos/MEFBidimensional (2).py`**
- Programa completo: funções de forma, derivadas, Jacobiano, matriz `B`, matriz
  constitutiva, integração de Gauss (quadrilátero) e Hammer (triângulo), montagem,
  condições de contorno, reações e pós-processamento em `Output.ogl`.
- O `Output.ogl` incluído foi **reproduzido byte a byte** ao executar este programa
  (12 nós, 5 quadriláteros, deslocamento vertical de −10000 no nó 12).

**`04_MEF_2D/3_historico/MEFBidimensional (1).py`**
- Versão intermédia **não executável**: `if (tipo_elemento == 1) # quadrilateral` sem `:`,
  `np.tranpose`, `mat_B[1,] =` incompleto. Guardada apenas como histórico do desenvolvimento.

---

## Notas sobre a organização

- Os nomes dos programas foram **mantidos** como o professor os forneceu; só as pastas
  e este README explicam a matéria de cada um.
- Foram removidos 2 ficheiros duplicados exatos (mesmo MD5): `Input (2).txt`
  (= `Input (1).txt`) e `Input (6).txt` (= `Input (5).txt`).
- Os PDFs foram renomeados para corrigir acentos quebrados no download
  (`Integrao_Numrica` → `Integracao_Numerica`, `Programao_TreliasPlanas` → `Programacao_Trelicas_Planas`)
  e para remover o sufixo `(1)` do download.


#   M E F  
 