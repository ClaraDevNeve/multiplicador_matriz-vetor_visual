import tkinter as tk
from tkinter import ttk
import math
from functools import partial

from backend import FIGURAS, aplicar_matriz, transformar_figura, multiplicar_matriz_vetor, fmt


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

C_GRID      = "#e8e6de"
C_AXIS      = "#b0aea6"
C_AXIS_LB   = "#999790"
C_ORIG_FILL = "#c8dff8"
C_ORIG_BD   = "#2b72c2"
C_TRSF_FILL = "#c6eaad"
C_TRSF_BD   = "#3e8c1a"
C_VTXHI_O   = "#ef9f27"
C_VTXHI_T   = "#c07020"
C_ARROW     = "#d06010"



class Celula(tk.Frame):
    def __init__(self, parent, **kw):
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

    def get(self):
        try:
            return float(self._var.get().replace(",", "."))
        except ValueError:
            return 0.0

    def set(self, v):
        self._var.set(str(round(float(v), 4)))

    def highlight(self, style):
        paletas = {
            "row":    (BLUE_BG,  BLUE_BD,  BLUE_TX),
            "col":    (AMBER_BG, AMBER_BD, AMBER_TX),
            "result": (GREEN_BG, GREEN_BD, GREEN_TX),
            None:     (BG2,      BORDER,   TEXT),
        }
        bg, bd, fg = paletas[style]
        self.config(bg=bg, highlightbackground=bd)
        self._entry.config(bg=bg, fg=fg)

    def readonly(self, val, style=None):
        self.set(val)
        self._entry.config(state="readonly")
        if style:
            self.highlight(style)



class Grade(tk.Frame):
    def __init__(self, parent, linhas, colunas, somente_leitura=False, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.linhas = linhas
        self.colunas = colunas
        self.celulas = []

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



class Canvas2D(tk.Frame):
    SIZE   = 360
    MARGIN = 36
    R_VTX  = 5
    R_HI   = 8

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, **kw)

        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text="Visualização",
                 font=("Helvetica", 10, "bold"), fg=TEXT, bg=BG).pack(side="left")

        tk.Label(hdr, text="Figura:", font=("Helvetica", 9),
                 fg=TEXT3, bg=BG).pack(side="right", padx=(12, 4))
        self._figura_var = tk.StringVar(value="Triângulo")
        sel = ttk.Combobox(hdr, textvariable=self._figura_var,
                           values=list(FIGURAS.keys()), width=10, state="readonly")
        sel.pack(side="right")
        sel.bind("<<ComboboxSelected>>", self._on_figura_changed)

        self.canvas = tk.Canvas(
            self, width=self.SIZE, height=self.SIZE,
            bg=WHITE, bd=0, highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.canvas.pack()

        leg = tk.Frame(self, bg=BG)
        leg.pack(fill="x", pady=(6, 2))
        self._legend_dot(leg, C_ORIG_FILL, C_ORIG_BD)
        tk.Label(leg, text="Original", font=("Helvetica", 9),
                 fg=TEXT2, bg=BG).pack(side="left", padx=(3, 16))
        self._legend_dot(leg, C_TRSF_FILL, C_TRSF_BD)
        tk.Label(leg, text="Transformada", font=("Helvetica", 9),
                 fg=TEXT2, bg=BG).pack(side="left", padx=(3, 0))

        self._scale   = 30.0
        self._orig    = None
        self._trsf    = None

        self._on_figura_changed_cb = None
        self._draw_empty()

    def set_figura_changed_callback(self, cb):
        self._on_figura_changed_cb = cb

    def _on_figura_changed(self, _=None):
        self._orig  = None
        self._trsf  = None
        self._draw_empty()
        if self._on_figura_changed_cb:
            self._on_figura_changed_cb()

    def get_figura(self):
        return FIGURAS[self._figura_var.get()]

    def _legend_dot(self, parent, fill, outline):
        c = tk.Canvas(parent, width=12, height=12, bg=BG, bd=0, highlightthickness=0)
        c.create_oval(1, 1, 11, 11, fill=fill, outline=outline, width=2)
        c.pack(side="left")


    def _to_canvas(self, wx, wy):
        cx = self.SIZE // 2 + wx * self._scale
        cy = self.SIZE // 2 - wy * self._scale
        return cx, cy

    def _calc_scale(self, point_lists):
        inner = self.SIZE - 2 * self.MARGIN
        all_pts = [v for pts in point_lists for v in pts]
        if not all_pts:
            return 30.0
        max_abs = max((abs(c) for pt in all_pts for c in pt), default=1.0)
        if max_abs == 0:
            max_abs = 1.0
        scale = (inner / 2) / max_abs
        return max(8.0, min(scale, 70.0))


    def _draw_empty(self):
        self.canvas.delete("all")
        self._draw_grid()
        self._draw_axes()

    def _draw_grid(self):
        S = self.SIZE
        cx = cy = S // 2
        step = self._scale
        x = cx
        while x <= S + step:
            self.canvas.create_line(x, 0, x, S, fill=C_GRID, width=1)
            ox = 2 * cx - x
            if ox >= 0:
                self.canvas.create_line(ox, 0, ox, S, fill=C_GRID, width=1)
            x += step
        y = cy
        while y <= S + step:
            self.canvas.create_line(0, y, S, y, fill=C_GRID, width=1)
            oy = 2 * cy - y
            if oy >= 0:
                self.canvas.create_line(0, oy, S, oy, fill=C_GRID, width=1)
            y += step

    def _draw_axes(self):
        S = self.SIZE
        cx = cy = S // 2
        m = self.MARGIN // 2
        self.canvas.create_line(m, cy, S - m, cy, fill=C_AXIS, width=2, arrow="last")
        self.canvas.create_line(cx, S - m, cx, m, fill=C_AXIS, width=2, arrow="last")
        self.canvas.create_text(S - m + 6, cy + 1, text="x", fill=C_AXIS_LB,
                                 font=("Helvetica", 9, "italic"), anchor="w")
        self.canvas.create_text(cx, m - 8, text="y", fill=C_AXIS_LB,
                                 font=("Helvetica", 9, "italic"), anchor="s")
        tick = 4
        i = 1
        while True:
            px = cx + i * self._scale
            if px > S - self.MARGIN:
                break
            for sign in (1, -1):
                vx = cx + sign * i * self._scale
                vy = cy - sign * i * self._scale
                lbl = str(i * sign) if sign == 1 else str(-i)
                lbly = str(i) if sign == 1 else str(-i)
                self.canvas.create_line(vx, cy - tick, vx, cy + tick, fill=C_AXIS, width=1)
                self.canvas.create_text(vx, cy + tick + 8, text=lbl,
                                         fill=C_AXIS_LB, font=("Helvetica", 7))
                self.canvas.create_line(cx - tick, vy, cx + tick, vy, fill=C_AXIS, width=1)
                self.canvas.create_text(cx - tick - 7, vy, text=lbly,
                                         fill=C_AXIS_LB, font=("Helvetica", 7), anchor="e")
            i += 1

    def _draw_poligono(self, vertices, fill, outline, dash=None):
        if len(vertices) < 2:
            return
        pts = [self._to_canvas(x, y) for x, y in vertices]
        flat = [c for p in pts for c in p]
        kw = dict(fill=fill, outline=outline, width=2)
        if dash:
            kw["dash"] = dash
        self.canvas.create_polygon(*flat, **kw)

    def _draw_vertices(self, vertices, fill, outline, r=None):
        if r is None:
            r = self.R_VTX
        for wx, wy in vertices:
            cx, cy = self._to_canvas(wx, wy)
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                     fill=fill, outline=outline, width=2)

    def _draw_seta(self, wx0, wy0, wx1, wy1, color=C_ARROW):
        cx0, cy0 = self._to_canvas(wx0, wy0)
        cx1, cy1 = self._to_canvas(wx1, wy1)
        if abs(cx1 - cx0) < 2 and abs(cy1 - cy0) < 2:
            return
        self.canvas.create_line(cx0, cy0, cx1, cy1,
                                 fill=color, width=1.5, dash=(5, 3),
                                 arrow="last", arrowshape=(10, 12, 4))


    def limpar(self):
        self._orig  = None
        self._trsf  = None
        self._scale = 30.0
        self._draw_empty()

    def mostrar_figura_completa(self, orig, trsf):
        self._orig = orig
        self._trsf = trsf
        self._redraw()

    def mostrar_vertice_ativo(self, orig, trsf_completo, vtx_orig, vtx_trsf):
        self._orig  = orig
        self._trsf  = trsf_completo
        self._vtx_orig = vtx_orig
        self._vtx_trsf = vtx_trsf
        self._redraw(destaque=True)

    def _redraw(self, destaque=False):
        pts = []
        if self._orig:
            pts.append(self._orig)
        if self._trsf:
            pts.append(self._trsf)
        if not pts:
            pts = [[(0, 0)]]
        self._scale = self._calc_scale(pts)

        self.canvas.delete("all")
        self._draw_grid()
        self._draw_axes()

        if not self._orig:
            return


        self._draw_poligono(self._orig, fill=C_ORIG_FILL, outline=C_ORIG_BD)
        self._draw_vertices(self._orig, fill=C_ORIG_FILL, outline=C_ORIG_BD)

        if self._trsf:
            dash = None if not destaque else (4, 3)
            self._draw_poligono(self._trsf, fill=C_TRSF_FILL, outline=C_TRSF_BD, dash=dash)
            self._draw_vertices(self._trsf, fill=C_TRSF_FILL, outline=C_TRSF_BD)
            if not destaque:
                for (ox, oy), (tx, ty) in zip(self._orig, self._trsf):
                    if (ox, oy) != (tx, ty):
                        self._draw_seta(ox, oy, tx, ty)


        if destaque and self._vtx_idx is not None:
            vi = self._vtx_idx
            ox, oy = self._vtx_orig_coords

            if self._vtx_trsf_coords:
                tx, ty = self._vtx_trsf_coords
                self._draw_seta(ox, oy, tx, ty, color=C_VTXHI_O)
                self._draw_vertice_destaque(tx, ty, AMBER_BG, C_VTXHI_T,
                                             label=f"v{vi+1}′ ({tx:.3g}, {ty:.3g})")
            elif self._vtx_partial_trsf:
                px, py = self._vtx_partial_trsf
                self._draw_seta(ox, oy, px, py, color=C_VTXHI_O)
                self._draw_vertice_destaque(px, py, AMBER_BG, C_VTXHI_T,
                                             label=f"x′={px:.3g}…")

            self._draw_vertice_destaque(ox, oy, AMBER_BG, C_VTXHI_O,
                                         label=f"v{vi+1} ({ox:.3g}, {oy:.3g})")



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transformações 2D — Multiplicação Matriz-Vetor Visual")
        self.resizable(False, False)
        self.config(bg=BG)

        self._mat          = None
        self._vertices     = []
        self._trsf_total   = []
        self._vtx_idx      = 0
        self._passos       = []
        self._passo_atual  = -1

        self._build_ui()
        self._valores_padrao()

    def _build_ui(self):
        tk.Label(self, text="Transformações 2D — Multiplicação Matriz-Vetor",
                 font=("Helvetica", 15, "bold"), fg=TEXT, bg=BG,
                 pady=10).pack()
        tk.Label(self,
                 text="A mesma matriz A é aplicada em cada vértice da figura  ·  "
                      "Como em engines de jogos e pipelines gráficas",
                 font=("Helvetica", 9), fg=TEXT3, bg=BG).pack()

        ctrl = tk.Frame(self, bg=BG, pady=8)
        ctrl.pack(fill="x", padx=20)

        tk.Label(ctrl, text="Transformação:", fg=TEXT2, bg=BG,
                 font=("Helvetica", 10)).pack(side="left")

        exemplos = [
            ("Escala ×2",     [[2, 0], [0, 2]]),
            ("Escala ×½",     [[0.5, 0], [0, 0.5]]),
            ("Rotação 45°",   [[round(math.cos(math.pi/4), 3), -round(math.sin(math.pi/4), 3)],
                               [round(math.sin(math.pi/4), 3),  round(math.cos(math.pi/4), 3)]]),
            ("Reflexão Y",    [[1, 0], [0, -1]]),
        ]
        for label, mat in exemplos:
            m = mat
            tk.Button(
                ctrl, text=label,
                command=lambda m=m: self._aplicar_exemplo(m),
                bg=BG2, fg=TEXT, relief="solid", bd=1,
                font=("Helvetica", 8), padx=6, pady=2, cursor="hand2",
            ).pack(side="left", padx=(4, 0))

        corpo = tk.Frame(self, bg=BG)
        corpo.pack(padx=20, pady=(4, 0))


        esq = tk.Frame(corpo, bg=BG)
        esq.pack(side="left", anchor="n")

        self.arena = tk.Frame(esq, bg=BG, pady=10)
        self.arena.pack()

        info = tk.Frame(esq, bg=BLUE_BG, bd=0,
                        highlightthickness=1, highlightbackground=BLUE_BD)
        info.pack(fill="x", pady=(0, 6))
        tk.Label(info,
                 text="  ℹ   O vetor exibido é o vértice selecionado  ·  "
                      "A = transformação  ·  vᵢ = vértice original  ·  b = vértice novo",
                 font=("Helvetica", 9), fg=BLUE_TX, bg=BLUE_BG,
                 pady=5, padx=4).pack(fill="x")

        tk.Frame(esq, bg=BORDER, height=1).pack(fill="x", pady=4)
        self.passo_frame = tk.Frame(esq, bg=BG2, bd=0,
                                    highlightthickness=1,
                                    highlightbackground=BORDER)
        self.passo_frame.pack(fill="x")

        self.lbl_passo_titulo = tk.Label(
            self.passo_frame, text="", font=("Helvetica", 10),
            fg=TEXT2, bg=BG2, anchor="w", padx=12, pady=6)
        self.lbl_passo_titulo.pack(fill="x")

        self.lbl_formula = tk.Label(
            self.passo_frame, text="Selecione uma transformação e clique em Calcular.",
            font=("Courier New", 11), fg=TEXT, bg=BG2,
            anchor="w", padx=12, pady=4, wraplength=440, justify="left")
        self.lbl_formula.pack(fill="x")

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

        tk.Frame(esq, bg=BORDER, height=1).pack(fill="x", pady=4)
        acao = tk.Frame(esq, bg=BG, pady=8)
        acao.pack(fill="x")

        tk.Button(acao, text="Limpar", command=self._limpar,
                  bg=WHITE, fg=TEXT, relief="solid", bd=1,
                  font=("Helvetica", 10), padx=10, pady=3,
                  cursor="hand2").pack(side="right", padx=(6, 0))
        tk.Button(acao, text="Calcular todas as transformações ▶",
                  command=self._calcular,
                  bg=ACCENT, fg=WHITE, relief="flat", bd=0,
                  font=("Helvetica", 11, "bold"), padx=14, pady=5,
                  cursor="hand2",
                  activebackground="#444441", activeforeground=WHITE,
                  ).pack(side="right")


        tk.Frame(corpo, bg=BORDER, width=1).pack(side="left", fill="y", padx=16)


        self.canvas2d = Canvas2D(corpo)
        self.canvas2d.set_figura_changed_callback(self._on_figura_changed)
        self.canvas2d.pack(side="left", anchor="n", pady=(6, 0))

        tk.Label(self, text="Edite a matriz A clicando nas células.",
                 font=("Helvetica", 9), fg=TEXT3, bg=BG, pady=6).pack()

        self._rebuild_grades()

    def _rebuild_grades(self):
        for w in self.arena.winfo_children():
            w.destroy()

        bloco_a = tk.Frame(self.arena, bg=BG)
        bloco_a.pack(side="left", anchor="n")
        tk.Label(bloco_a, text="Matriz A  (2×2)", font=("Helvetica", 9),
                 fg=TEXT3, bg=BG).pack(anchor="w")
        self.grade_mat = Grade(bloco_a, 2, 2)
        self.grade_mat.pack()

        tk.Label(self.arena, text="·", font=("Helvetica", 24),
                 fg=TEXT3, bg=BG).pack(side="left", padx=8)

        bloco_v = tk.Frame(self.arena, bg=BG)
        bloco_v.pack(side="left", anchor="n")
        self.lbl_vec_header = tk.Label(bloco_v, text="Vértice vᵢ", font=("Helvetica", 9),
                                        fg=TEXT3, bg=BG)
        self.lbl_vec_header.pack(anchor="w")
        self.grade_vec = Grade(bloco_v, 2, 1)
        self.grade_vec.pack()

        tk.Label(self.arena, text="=", font=("Helvetica", 22),
                 fg=TEXT3, bg=BG).pack(side="left", padx=8)

        bloco_r = tk.Frame(self.arena, bg=BG)
        bloco_r.pack(side="left", anchor="n")
        tk.Label(bloco_r, text="Resultado b", font=("Helvetica", 9),
                 fg=TEXT3, bg=BG).pack(anchor="w")
        self.grade_res = Grade(bloco_r, 2, 1, somente_leitura=True)
        for r in range(2):
            cel = self.grade_res.celulas[r][0]
            cel.set(0)
            cel._entry.config(state="readonly", fg=TEXT3)
        self.grade_res.pack()

    def _valores_padrao(self):
        self.grade_mat.set_dados([[1, 0], [0, 1]])
        self._vertices = self.canvas2d.get_figura()
        self._atualizar_grade_vec(0)

    def _aplicar_exemplo(self, mat):
        self.grade_mat.set_dados(mat)
        self._reset_calculo()

    def _on_figura_changed(self):
        self._vertices = self.canvas2d.get_figura()
        self._reset_calculo()
        self._atualizar_grade_vec(0)

    def _limpar(self):
        self.grade_mat.set_dados([[0, 0], [0, 0]])
        self._reset_calculo()
        self.canvas2d.limpar()

    def _reset_calculo(self):
        self._trsf_total  = []
        self._vtx_idx     = 0
        self._passos      = []
        self._passo_atual = -1
        self._limpar_highlights()
        for r in range(2):
            cel = self.grade_res.celulas[r][0]
            cel._entry.config(state="normal")
            cel.set(0)
            cel._entry.config(state="readonly", fg=TEXT3)
        self.lbl_passo_titulo.config(text="")
        self.lbl_formula.config(text="Selecione uma transformação e clique em Calcular.")
        self.btn_prev.config(state="disabled")
        self.btn_next.config(state="disabled")
        self._atualizar_dots()

    def _atualizar_grade_vec(self, idx):
        if idx < len(self._vertices):
            vx, vy = self._vertices[idx]
            self.grade_vec.set_dados([[vx], [vy]])
            n = len(self._vertices)
            self.lbl_vec_header.config(text=f"Vértice v{idx+1}  (de {n})")

    def _calcular(self):
        mat = self.grade_mat.get_dados()
        self._mat = mat
        self._vertices = self.canvas2d.get_figura()

        self._trsf_total = transformar_figura(mat, self._vertices)

        self.canvas2d.mostrar_figura_completa(self._vertices, self._trsf_total)
        n = len(self._vertices)

        self._vtx_idx = 0
        self._iniciar_passos_vertice(0)

        self.lbl_passo_titulo.config(
            text=f"✓  {n} vértices transformados  —  veja o cálculo de cada um abaixo")
        self.lbl_formula.config(
            text="Use Anterior/Próximo para ver os passos do cálculo.")

    def _iniciar_passos_vertice(self, idx):
        self._vtx_idx = idx
        vx, vy = self._vertices[idx]
        self._atualizar_grade_vec(idx)
        _, self._passos = multiplicar_matriz_vetor(self._mat, [vx, vy])

        tx, ty = self._trsf_total[idx]
        for r in range(2):
            cel = self.grade_res.celulas[r][0]
            cel._entry.config(state="normal")
            cel.set([tx, ty][r])
            cel._entry.config(state="readonly")
            cel.highlight(None)

        self._passo_atual = 0
        self._renderizar_passo()

    def _proximo(self):
        if self._passo_atual < len(self._passos) - 1:
            self._passo_atual += 1
            self._renderizar_passo()

    def _prev(self):
        if self._passo_atual > 0:
            self._passo_atual -= 1
            self._renderizar_passo()


    def _renderizar_passo(self):
        if self._passo_atual < 0 or self._passo_atual >= len(self._passos):
            return

        self._limpar_highlights()
        step = self._passos[self._passo_atual]

        self.btn_prev.config(state="normal" if self._passo_atual > 0 else "disabled")
        self.btn_next.config(
            state="normal" if self._passo_atual < len(self._passos) - 1 else "disabled")
        self._atualizar_dots()

        vi = self._vtx_idx
        vx, vy = self._vertices[vi]
        tx, ty = self._trsf_total[vi]

        if step["tipo"] == "pronto":
            self.lbl_passo_titulo.config(
                text=f"✓  Vértice {vi + 1}  calculado")
            self.lbl_formula.config(
                text=f"v{vi+1} = ({vx:.3g}, {vy:.3g})  →  "
                     f"A·v{vi+1} = ({tx:.3g}, {ty:.3g})\n"
                     f"Navegue pelos vértices com ← → para ver os outros.")
            for r in range(2):
                self.grade_res.celulas[r][0].highlight("result")

            self.canvas2d.mostrar_vertice_ativo(
                self._vertices, self._trsf_total,
                vi, (vx, vy), (tx, ty),
            )
            self.canvas2d.lbl_status.config(
                text=f"v{vi+1} ({vx:.3g}, {vy:.3g})  →  b ({tx:.3g}, {ty:.3g})")
            return

        linha = step["linha"]
        termos = step["termos"]

        coordenada = "x′  (nova coord. x)" if linha == 0 else "y′  (nova coord. y)"
        self.lbl_passo_titulo.config(
            text=f"Vértice {vi + 1}  —  Passo {self._passo_atual + 1} "
                 f"de {len(self._passos) - 1}  —  calculando {coordenada}")

        for c in range(2):
            self.grade_mat.celulas[linha][c].highlight("row")
            self.grade_vec.celulas[c][0].highlight("col")
        self.grade_res.celulas[linha][0].highlight("result")

        partes = [f"{fmt(a)} × {fmt(x)}" for a, x, *_ in termos]
        total = termos[-1][3]
        formula = (f"b[{linha + 1}]  =  " +
                   "  +  ".join(partes) +
                   f"  =  {fmt(total)}")
        self.lbl_formula.config(text=formula)

        if linha == 0:
            self.canvas2d.mostrar_vertice_ativo(
                self._vertices, None,
                vi, (vx, vy), None, vtx_partial=partial,
            )
            self.canvas2d.lbl_status.config(
                text=f"v{vi+1} ({vx:.3g}, {vy:.3g})  →  x′ = {total:.3g},  y′ = ?")
        else:
            self.canvas2d.mostrar_vertice_ativo(
                self._vertices, self._trsf_total,
                vi, (vx, vy), (tx, ty),
            )
            self.canvas2d.lbl_status.config(
                text=f"v{vi+1} ({vx:.3g}, {vy:.3g})  →  b ({tx:.3g}, {ty:.3g})")

    def _limpar_highlights(self):
        self.grade_mat.limpar_highlights()
        self.grade_vec.limpar_highlights()
        self.grade_res.limpar_highlights()

    def _atualizar_dots(self):
        for w in self.dots_frame.winfo_children():
            w.destroy()
        for i in range(len(self._passos)):
            cor = ACCENT if i == self._passo_atual else BORDER
            tk.Label(self.dots_frame, text="●", fg=cor, bg=BG2,
                     font=("Helvetica", 9)).pack(side="left", padx=1)
