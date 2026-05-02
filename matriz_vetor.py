import tkinter as tk
from tkinter import ttk, messagebox
import random


# ─── Paleta de cores ───────────────────────────────────────────────────────────
BG        = "#f9f9f7"
BG2       = "#f1efe8"
BORDER    = "#d3d1c7"
TEXT      = "#2c2c2a"
TEXT2     = "#5f5e5a"
TEXT3     = "#888780"

BLUE_BG   = "#e6f1fb"
BLUE_BD   = "#85b7eb"
BLUE_TX   = "#0c447c"

AMBER_BG  = "#faeeda"
AMBER_BD  = "#ef9f27"
AMBER_TX  = "#633806"

GREEN_BG  = "#eaf3de"
GREEN_BD  = "#639922"
GREEN_TX  = "#27500a"

WHITE     = "#ffffff"
ACCENT    = "#2c2c2a"


# ─── Lógica do cálculo ─────────────────────────────────────────────────────────
def multiplicar_matriz_vetor(mat, vec):
    """Retorna (resultado, passos)."""
    R = len(mat)
    C = len(mat[0])
    resultado = []
    passos = []

    for r in range(R):
        termos = []
        soma = 0.0
        for c in range(C):
            a = mat[r][c]
            x = vec[c]
            soma += a * x
            termos.append((a, x, c, round(soma, 6)))
        resultado.append(round(soma, 6))
        passos.append({
            "tipo": "linha",
            "linha": r,
            "termos": termos,
            "resultado": round(soma, 6),
        })

    passos.append({"tipo": "pronto", "resultado": resultado})
    return resultado, passos


def fmt(v):
    n = round(float(v), 4)
    s = f"({n})" if n < 0 else str(n)
    return s


# ─── Widget de célula editável ─────────────────────────────────────────────────
class Celula(tk.Frame):
    def __init__(self, parent, width=52, **kw):
        super().__init__(parent, bg=BG2, bd=0, highlightthickness=1,
                         highlightbackground=BORDER, **kw)
        self._var = tk.StringVar(value="0")
        self._entry = tk.Entry(
            self, textvariable=self._var, width=5,
            font=("Courier New", 13), bd=0, relief="flat",
            justify="center", bg=BG2, fg=TEXT,
            insertbackground=TEXT, highlightthickness=0,
        )
        self._entry.pack(padx=4, pady=6)
        self._normal_bg = BG2
        self._normal_bd = BORDER

    def get(self):
        try:
            return float(self._var.get().replace(",", "."))
        except ValueError:
            return 0.0

    def set(self, v):
        self._var.set(str(round(float(v), 4)))

    def highlight(self, style):
        """style: 'row' | 'col' | 'result' | None"""
        paletas = {
            "row":    (BLUE_BG,  BLUE_BD,  BLUE_TX),
            "col":    (AMBER_BG, AMBER_BD, AMBER_TX),
            "result": (GREEN_BG, GREEN_BD, GREEN_TX),
            None:     (BG2,      BORDER,   TEXT),
        }
        bg, bd, fg = paletas[style]
        self.config(bg=bg, highlightbackground=bd)
        self._entry.config(bg=bg, fg=fg)
        self._normal_bg, self._normal_bd = bg, bd

    def readonly(self, val, style=None):
        """Torna a célula somente-leitura e mostra o valor."""
        self.set(val)
        self._entry.config(state="readonly")
        if style:
            self.highlight(style)


# ─── Grade de células ──────────────────────────────────────────────────────────
class Grade(tk.Frame):
    def __init__(self, parent, linhas, colunas, somente_leitura=False, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.linhas = linhas
        self.colunas = colunas
        self.celulas = []

        # Colchete esquerdo
        tk.Label(self, text="[", font=("Courier New", 28, "bold"),
                 fg=TEXT2, bg=BG).grid(row=0, column=0, rowspan=linhas, padx=(0, 4))

        for r in range(linhas):
            linha = []
            for c in range(colunas):
                cel = Celula(self)
                if somente_leitura:
                    cel._entry.config(state="readonly")
                cel.grid(row=r, column=c + 1, padx=3, pady=3)
                linha.append(cel)
            self.celulas.append(linha)

        # Colchete direito
        tk.Label(self, text="]", font=("Courier New", 28, "bold"),
                 fg=TEXT2, bg=BG).grid(row=0, column=colunas + 1, rowspan=linhas, padx=(4, 0))

    def get_dados(self):
        dados = []
        for r in range(self.linhas):
            if self.colunas == 1:
                dados.append(self.celulas[r][0].get())
            else:
                dados.append([self.celulas[r][c].get() for c in range(self.colunas)])
        return dados

    def set_dados(self, dados):
        for r in range(self.linhas):
            for c in range(self.colunas):
                v = dados[r][c] if isinstance(dados[r], list) else dados[r]
                self.celulas[r][c].set(v)

    def limpar_highlights(self):
        for r in range(self.linhas):
            for c in range(self.colunas):
                self.celulas[r][c].highlight(None)


# ─── Janela principal ──────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multiplicador Matriz-Vetor Visual")
        self.resizable(False, False)
        self.config(bg=BG)

        self.R = 3
        self.C = 3
        self.passos = []
        self.passo_atual = -1

        self._build_ui()
        self._rebuild_grades()
        self._valores_padrao()

    # ── Construção da UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Título
        tk.Label(self, text="Multiplicador Matriz-Vetor Visual",
                 font=("Helvetica", 16, "bold"), fg=TEXT, bg=BG,
                 pady=12).pack()

        # Barra de controles
        ctrl = tk.Frame(self, bg=BG, pady=6)
        ctrl.pack(fill="x", padx=20)

        tk.Label(ctrl, text="Linhas:", fg=TEXT2, bg=BG,
                 font=("Helvetica", 11)).pack(side="left")
        self.sel_linhas = ttk.Combobox(ctrl, values=["2", "3", "4"],
                                        width=3, state="readonly")
        self.sel_linhas.set("3")
        self.sel_linhas.pack(side="left", padx=(4, 12))
        self.sel_linhas.bind("<<ComboboxSelected>>", self._on_resize)

        tk.Label(ctrl, text="Colunas:", fg=TEXT2, bg=BG,
                 font=("Helvetica", 11)).pack(side="left")
        self.sel_colunas = ttk.Combobox(ctrl, values=["2", "3", "4"],
                                         width=3, state="readonly")
        self.sel_colunas.set("3")
        self.sel_colunas.pack(side="left", padx=(4, 0))
        self.sel_colunas.bind("<<ComboboxSelected>>", self._on_resize)

        tk.Button(ctrl, text="Aleatório", command=self._aleatorio,
                  bg=WHITE, fg=TEXT, relief="solid", bd=1,
                  font=("Helvetica", 11), padx=10, pady=3,
                  cursor="hand2").pack(side="right", padx=(6, 0))
        tk.Button(ctrl, text="Limpar", command=self._limpar,
                  bg=WHITE, fg=TEXT, relief="solid", bd=1,
                  font=("Helvetica", 11), padx=10, pady=3,
                  cursor="hand2").pack(side="right", padx=(6, 0))
        tk.Button(ctrl, text="Calcular ▶", command=self._calcular,
                  bg=ACCENT, fg=WHITE, relief="flat", bd=0,
                  font=("Helvetica", 11, "bold"), padx=14, pady=4,
                  cursor="hand2", activebackground="#444441", activeforeground=WHITE,
                  ).pack(side="right", padx=(6, 0))

        # Área da arena (matriz × vetor = resultado)
        self.arena = tk.Frame(self, bg=BG, pady=10)
        self.arena.pack(padx=20)

        # Separador
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20, pady=4)

        # Painel de passo
        self.passo_frame = tk.Frame(self, bg=BG2, bd=0,
                                    highlightthickness=1,
                                    highlightbackground=BORDER)
        self.passo_frame.pack(fill="x", padx=20, pady=8)

        self.lbl_passo_titulo = tk.Label(
            self.passo_frame, text="", font=("Helvetica", 10),
            fg=TEXT2, bg=BG2, anchor="w", padx=12, pady=6)
        self.lbl_passo_titulo.pack(fill="x")

        self.lbl_formula = tk.Label(
            self.passo_frame, text="Clique em Calcular para iniciar.",
            font=("Courier New", 12), fg=TEXT, bg=BG2,
            anchor="w", padx=12, pady=4, wraplength=640, justify="left")
        self.lbl_formula.pack(fill="x")

        # Navegação
        nav = tk.Frame(self.passo_frame, bg=BG2, pady=6)
        nav.pack(fill="x", padx=12)

        self.btn_prev = tk.Button(nav, text="← Anterior", command=self._prev,
                                   bg=WHITE, fg=TEXT, relief="solid", bd=1,
                                   font=("Helvetica", 10), padx=8, pady=2,
                                   cursor="hand2", state="disabled")
        self.btn_prev.pack(side="left")

        self.dots_frame = tk.Frame(nav, bg=BG2)
        self.dots_frame.pack(side="left", padx=12)

        self.btn_next = tk.Button(nav, text="Próximo →", command=self._proximo,
                                   bg=WHITE, fg=TEXT, relief="solid", bd=1,
                                   font=("Helvetica", 10), padx=8, pady=2,
                                   cursor="hand2", state="disabled")
        self.btn_next.pack(side="right")

        # Rodapé
        tk.Label(self, text="Edite os valores clicando nas células.",
                 font=("Helvetica", 9), fg=TEXT3, bg=BG, pady=6).pack()

    # ── Grades ─────────────────────────────────────────────────────────────────
    def _rebuild_grades(self):
        for w in self.arena.winfo_children():
            w.destroy()

        # Rótulo A
        self._bloco(self.arena, f"Matriz A  ({self.R}×{self.C})")

        self.grade_mat = Grade(self.arena, self.R, self.C)
        self.grade_mat.pack(side="left", padx=(0, 6))

        # ×
        tk.Label(self.arena, text="×", font=("Helvetica", 22),
                 fg=TEXT3, bg=BG).pack(side="left", padx=8)

        # Rótulo x
        self._bloco(self.arena, f"Vetor x  ({self.C}×1)")

        self.grade_vec = Grade(self.arena, self.C, 1)
        self.grade_vec.pack(side="left", padx=(0, 6))

        # =
        tk.Label(self.arena, text="=", font=("Helvetica", 22),
                 fg=TEXT3, bg=BG).pack(side="left", padx=8)

        # Rótulo b
        self._bloco(self.arena, f"Resultado b  ({self.R}×1)")

        self.grade_res = Grade(self.arena, self.R, 1, somente_leitura=True)
        for r in range(self.R):
            self.grade_res.celulas[r][0].set(0)
            self.grade_res.celulas[r][0]._entry.config(state="readonly",
                                                        fg=TEXT3)
        self.grade_res.pack(side="left")

    def _bloco(self, parent, texto):
        """Empilha um rótulo acima de um futuro widget — aqui só adiciona texto."""
        tk.Label(parent, text=texto, font=("Helvetica", 9),
                 fg=TEXT3, bg=BG).pack(side="left", anchor="n", pady=(0, 4))

    # ── Ações ──────────────────────────────────────────────────────────────────
    def _on_resize(self, _=None):
        self.R = int(self.sel_linhas.get())
        self.C = int(self.sel_colunas.get())
        self._rebuild_grades()
        self._reset_passos()

    def _valores_padrao(self):
        mat = [[2, 0, 1], [1, 3, -1], [0, 2, 4]]
        vec = [1, 2, -1]
        self.grade_mat.set_dados(mat)
        self.grade_vec.set_dados([[v] for v in vec])

    def _aleatorio(self):
        mat = [[round(random.uniform(-5, 5), 1) for _ in range(self.C)]
               for _ in range(self.R)]
        vec = [[round(random.uniform(-3, 3), 1)] for _ in range(self.C)]
        self.grade_mat.set_dados(mat)
        self.grade_vec.set_dados(vec)
        self._reset_passos()

    def _limpar(self):
        self.grade_mat.set_dados([[0] * self.C for _ in range(self.R)])
        self.grade_vec.set_dados([[0] for _ in range(self.C)])
        self._reset_passos()

    def _reset_passos(self):
        self.passos = []
        self.passo_atual = -1
        self._limpar_highlights()
        for r in range(self.R):
            cel = self.grade_res.celulas[r][0]
            cel._entry.config(state="normal")
            cel.set(0)
            cel._entry.config(state="readonly", fg=TEXT3)
        self.lbl_passo_titulo.config(text="")
        self.lbl_formula.config(text="Clique em Calcular para iniciar.")
        self.btn_prev.config(state="disabled")
        self.btn_next.config(state="disabled")
        self._atualizar_dots()

    def _calcular(self):
        mat = self.grade_mat.get_dados()
        vec_raw = self.grade_vec.get_dados()
        vec = [v[0] if isinstance(v, list) else v for v in vec_raw]

        resultado, self.passos = multiplicar_matriz_vetor(mat, vec)

        # Preenche resultados na grade
        for r in range(self.R):
            cel = self.grade_res.celulas[r][0]
            cel._entry.config(state="normal")
            cel.set(resultado[r])
            cel._entry.config(state="readonly")
            cel.highlight(None)

        self.passo_atual = 0
        self._renderizar_passo()

    def _proximo(self):
        if self.passo_atual < len(self.passos) - 1:
            self.passo_atual += 1
            self._renderizar_passo()

    def _prev(self):
        if self.passo_atual > 0:
            self.passo_atual -= 1
            self._renderizar_passo()

    # ── Renderização de passo ──────────────────────────────────────────────────
    def _renderizar_passo(self):
        if self.passo_atual < 0 or self.passo_atual >= len(self.passos):
            return

        self._limpar_highlights()
        step = self.passos[self.passo_atual]

        self.btn_prev.config(state="normal" if self.passo_atual > 0 else "disabled")
        self.btn_next.config(
            state="normal" if self.passo_atual < len(self.passos) - 1 else "disabled")
        self._atualizar_dots()

        if step["tipo"] == "pronto":
            self.lbl_passo_titulo.config(text="✓  Cálculo completo")
            self.lbl_formula.config(
                text=f"Todos os {self.R} elementos do vetor resultado foram calculados.")
            for r in range(self.R):
                self.grade_res.celulas[r][0].highlight("result")
            return

        linha = step["linha"]
        termos = step["termos"]

        self.lbl_passo_titulo.config(
            text=f"Passo {self.passo_atual + 1} de {len(self.passos) - 1}"
                 f"  —  calculando b[{linha + 1}]  (linha {linha + 1} × vetor)")

        # Highlights
        for c in range(self.C):
            self.grade_mat.celulas[linha][c].highlight("row")
            self.grade_vec.celulas[c][0].highlight("col")
        self.grade_res.celulas[linha][0].highlight("result")

        # Fórmula
        partes = [f"{fmt(a)} × {fmt(x)}" for a, x, *_ in termos]
        total = termos[-1][3]  # runSum final
        formula = (f"b[{linha + 1}]  =  " +
                   "  +  ".join(partes) +
                   f"  =  {fmt(total)}")
        self.lbl_formula.config(text=formula)

    def _limpar_highlights(self):
        self.grade_mat.limpar_highlights()
        self.grade_vec.limpar_highlights()
        self.grade_res.limpar_highlights()

    def _atualizar_dots(self):
        for w in self.dots_frame.winfo_children():
            w.destroy()
        n = len(self.passos)
        for i in range(n):
            cor = ACCENT if i == self.passo_atual else BORDER
            tk.Label(self.dots_frame, text="●", fg=cor, bg=BG2,
                     font=("Helvetica", 9)).pack(side="left", padx=1)


# ─── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
