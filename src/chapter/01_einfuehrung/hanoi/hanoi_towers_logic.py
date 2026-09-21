from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import clear_output, display
from matplotlib.patches import Rectangle

PEG_NAMES = ("A", "B", "C")


@dataclass(frozen=True)
class Move:
    index: int
    disc: int
    src: str
    dst: str
    call_depth: int
    pegs_after: Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[int, ...]]
    note: str


@dataclass
class _Recorder:
    """Collects one Move per disc placement while the recursion runs."""
    pegs: Dict[str, List[int]]
    moves: List[Move] = field(default_factory=list)
    call_counter: int = 0

    def move_disc(self, src: str, dst: str, depth: int) -> None:
        # The disc moved by a hanoi(1, ...) call is whatever sits on top
        # of the source peg, not literally disc "1".
        disc = self.pegs[src].pop()
        self.pegs[dst].append(disc)
        self.moves.append(
            Move(
                index=len(self.moves),
                disc=disc,
                src=src,
                dst=dst,
                call_depth=depth,
                pegs_after=(
                    tuple(self.pegs["A"]),
                    tuple(self.pegs["B"]),
                    tuple(self.pegs["C"]),
                ),
                note=f"hanoi(1, {src}, ?, {dst}): move disc {disc} directly",
            )
        )


def hanoi_recursive(n: int, src: str, aux: str, dst: str,
                    recorder: _Recorder, depth: int = 0) -> None:
    """Lecture form:

    void hanoi(int n, char A, char B, char C) {
        if (n == 1) { move A -> C; return; }
        hanoi(n - 1, A, C, B);
        hanoi(1, A, B, C);
        hanoi(n - 1, B, A, C);
    }
    """
    if n == 1:
        recorder.move_disc(src, dst, depth)
        return
    hanoi_recursive(n - 1, src, dst, aux, recorder, depth + 1)
    hanoi_recursive(1, src, aux, dst, recorder, depth + 1)
    hanoi_recursive(n - 1, aux, src, dst, recorder, depth + 1)


def solve_hanoi(num_discs: int) -> List[Move]:
    """Run the recursive algorithm and return the full list of disc moves."""
    pegs = {
        "A": list(range(num_discs, 0, -1)),
        "B": [],
        "C": [],
    }
    recorder = _Recorder(pegs=pegs)
    if num_discs > 0:
        hanoi_recursive(num_discs, "A", "B", "C", recorder)
    return recorder.moves


def initial_pegs(num_discs: int) -> Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[int, ...]]:
    return (tuple(range(num_discs, 0, -1)), (), ())


def draw_towers(ax: Any, pegs: Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[int, ...]],
                num_discs: int, highlight: Optional[Tuple[str, int]] = None) -> None:
    """Draw the three pegs with their current discs.

    highlight is an optional (peg_name, disc) pair drawn with a red outline.
    """
    peg_x = {"A": 0, "B": 1, "C": 2}
    peg_height = num_discs + 1
    disc_h = 0.8
    max_width = 0.9

    for name, x in peg_x.items():
        ax.add_patch(Rectangle(
            (x - 0.03, 0), 0.06, peg_height,
            facecolor="#6d4c41", edgecolor="none", zorder=1))
        ax.text(x, -0.6, name, ha="center", va="top",
                fontsize=12, fontweight="bold")

    cmap = plt.cm.viridis
    for name, discs in zip(PEG_NAMES, pegs):
        x = peg_x[name]
        for level, disc in enumerate(discs):
            width = max_width * disc / num_discs
            color = cmap(disc / num_discs)
            is_highlighted = highlight is not None and highlight == (
                name, disc)
            ax.add_patch(Rectangle(
                (x - width / 2, level * disc_h), width, disc_h * 0.9,
                facecolor=color,
                edgecolor="red" if is_highlighted else "#263238",
                linewidth=2.5 if is_highlighted else 1.0,
                zorder=2,
            ))
            ax.text(x, level * disc_h + disc_h * 0.45, str(disc),
                    ha="center", va="center", fontsize=8, color="white",
                    fontweight="bold", zorder=3)

    ax.set_xlim(-0.7, 2.7)
    ax.set_ylim(-1.0, peg_height + 0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def create_visualizer() -> Dict[str, Any]:
    plt.rcParams["figure.figsize"] = (7, 5)

    discs_input = widgets.IntSlider(
        value=4, min=1, max=8, description="Discs:",
        continuous_update=False)
    apply_button = widgets.Button(
        description="Apply / Reset", button_style="primary", icon="refresh")
    prev_button = widgets.Button(description="Previous", icon="arrow-left")
    next_button = widgets.Button(
        description="Next", button_style="info", icon="arrow-right")
    complete_button = widgets.Button(
        description="Show final state", icon="forward")
    play = widgets.Play(
        value=0, min=0, max=1, interval=500, description="Play")
    step_slider = widgets.IntSlider(
        value=0, min=0, max=1, description="Step:",
        continuous_update=False, layout=widgets.Layout(width="620px"))
    widgets.jslink((play, "value"), (step_slider, "value"))

    summary_output, plot_output, trace_output = (
        widgets.Output(), widgets.Output(), widgets.Output())
    state: Dict[str, Any] = {"moves": [], "num_discs": 0}

    def apply_settings(_=None) -> None:
        num_discs = discs_input.value
        state["num_discs"] = num_discs
        state["moves"] = solve_hanoi(num_discs)
        max_step = len(state["moves"])
        step_slider.max = max_step
        play.max = max_step
        step_slider.value = 0
        render()

    def render(_=None) -> None:
        moves = state["moves"]
        num_discs = state["num_discs"]
        k = min(step_slider.value, len(moves))

        if k == 0:
            pegs = initial_pegs(num_discs)
            highlight = None
            current_move = None
        else:
            current_move = moves[k - 1]
            pegs = current_move.pegs_after
            highlight = (current_move.dst, current_move.disc)

        with summary_output:
            clear_output(wait=True)
            print(f"Step {k} of {len(moves)}")
            if current_move is None:
                print(f"Initial state: all {num_discs} discs on peg A")
            else:
                print(
                    f"Move {current_move.index + 1}: disc "
                    f"{current_move.disc} from {current_move.src} "
                    f"to {current_move.dst}")
                print(f"Recursion depth: {current_move.call_depth}")
                print(current_move.note)
            print(f"Total moves for {num_discs} discs: "
                  f"2^{num_discs} - 1 = {2 ** num_discs - 1}")

        with plot_output:
            clear_output(wait=True)
            fig, ax = plt.subplots()
            draw_towers(ax, pegs, num_discs, highlight)
            title = "Towers of Hanoi: initial state" if current_move is None \
                else f"Towers of Hanoi: move {current_move.index + 1}"
            ax.set_title(title)
            plt.show()

        with trace_output:
            clear_output(wait=True)
            print(f"{'i':>4} | {'disc':>4} | {'from':>4} | {'to':>4} | {'depth':>5}")
            print("-" * 34)
            for move in moves[:k]:
                print(
                    f"{move.index + 1:>4} | {move.disc:>4} | "
                    f"{move.src:>4} | {move.dst:>4} | {move.call_depth:>5}")

        prev_button.disabled = k == 0
        next_button.disabled = k == len(moves)

    apply_button.on_click(apply_settings)
    prev_button.on_click(lambda _: setattr(
        step_slider, "value", max(step_slider.min, step_slider.value - 1)))
    next_button.on_click(lambda _: setattr(
        step_slider, "value", min(step_slider.max, step_slider.value + 1)))
    complete_button.on_click(lambda _: setattr(
        step_slider, "value", step_slider.max))
    step_slider.observe(render, names="value")

    display(
        widgets.VBox([
            widgets.HTML("<b>Number of discs</b>"),
            discs_input,
            widgets.HBox([apply_button, prev_button,
                         next_button, complete_button]),
            widgets.HBox([play, step_slider]),
        ]),
        summary_output,
        plot_output,
        widgets.HTML("<b>Move log up to current step</b>"),
        trace_output,
    )
    apply_settings()
    return {
        "discs_input": discs_input,
        "apply_button": apply_button,
        "prev_button": prev_button,
        "next_button": next_button,
        "complete_button": complete_button,
        "step_slider": step_slider,
        "summary_output": summary_output,
        "plot_output": plot_output,
        "trace_output": trace_output,
        "state": state,
    }


__all__ = ["Move", "solve_hanoi", "initial_pegs",
           "draw_towers", "create_visualizer"]


if __name__ == "__main__":
    moves = solve_hanoi(3)
    assert len(moves) == 2 ** 3 - 1
    assert [(m.disc, m.src, m.dst) for m in moves] == [
        (1, "A", "C"), (2, "A", "B"), (1, "C", "B"),
        (3, "A", "C"), (1, "B", "A"), (2, "B", "C"), (1, "A", "C"),
    ]
    for count in range(1, 6):
        assert len(solve_hanoi(count)) == 2 ** count - 1
    print("Algorithm checks passed.")
