from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import clear_output, display
from matplotlib.patches import Rectangle


@dataclass(frozen=True)
class Step:
    index: int
    x: int
    y: int
    error: float
    move_x: bool
    move_y: bool
    next_x: Optional[int]
    next_y: Optional[int]
    next_error: Optional[float]
    note: str


def bresenham_steps(x0: int, y0: int, x1: int, y1: int) -> List[Step]:
    x, y = int(x0), int(y0)
    x_end, y_end = int(x1), int(y1)

    dx = abs(x_end - x)
    dy = abs(y_end - y)
    sx = 1 if x < x_end else -1
    sy = 1 if y < y_end else -1

    # Lecture form:
    # error = dx / 2
    # while x < xend:
    #     x = x + 1
    #     error = error - dy
    #     if error < 0:
    #         y = y + 1
    #         error = error + dx
    #     setpixel(x, y)
    trace: List[Step] = []

    if dx >= dy:
        error = dx / 2.0
        while x != x_end:
            current_x, current_y, current_error = x, y, error
            next_x, next_y, next_error = x, y, error
            move_x = False
            move_y = False
            changes: List[str] = []

            next_x += sx
            next_error -= dy
            move_x = True
            changes.append(
                f"move x; error = error({current_error:g}) - dy ({dy})")

            if next_error < 0:
                next_y += sy
                correction_error = next_error
                next_error += dx
                move_y = True
                changes.append(
                    f"Hint: error < 0; move y; "
                    f"error = error({correction_error:g}) + dx ({dx})")

            trace.append(
                Step(
                    len(trace),
                    current_x,
                    current_y,
                    current_error,
                    move_x,
                    move_y,
                    next_x,
                    next_y,
                    next_error,
                    "; ".join(changes),
                )
            )

            x, y, error = next_x, next_y, next_error

        trace.append(
            Step(
                len(trace),
                x,
                y,
                error,
                False,
                False,
                None,
                None,
                None,
                "Endpoint reached; rasterization is complete.",
            )
        )
    else:
        error = dy / 2.0
        while y != y_end:
            current_x, current_y, current_error = x, y, error
            next_x, next_y, next_error = x, y, error
            move_x = False
            move_y = False
            changes: List[str] = []

            next_y += sy
            next_error -= dx
            move_y = True
            changes.append(
                f"move y; error = error({current_error:g}) - dx ({dx})")

            if next_error < 0:
                next_x += sx
                correction_error = next_error
                next_error += dy
                move_x = True
                changes.append(
                    f"Hint: error < 0; move x; "
                    f"error = error({correction_error:g}) + dy ({dy})")

            trace.append(
                Step(
                    len(trace),
                    current_x,
                    current_y,
                    current_error,
                    move_x,
                    move_y,
                    next_x,
                    next_y,
                    next_error,
                    "; ".join(changes),
                )
            )

            x, y, error = next_x, next_y, next_error

        trace.append(
            Step(
                len(trace),
                x,
                y,
                error,
                False,
                False,
                None,
                None,
                None,
                "Endpoint reached; rasterization is complete.",
            )
        )

    return trace


def draw_cell(
    ax: Any,
    x: int,
    y: int,
    facecolor: str = "none",
    edgecolor: str = "black",
    alpha: float = 1.0,
    linewidth: float = 1.0,
    zorder: int = 1,
) -> None:
    """Draw a true 1 by 1 raster cell centered at integer coordinate (x, y)."""
    ax.add_patch(
        Rectangle(
            (x - 0.5, y - 0.5),
            1.0,
            1.0,
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
            alpha=alpha,
            zorder=zorder,
        )
    )


def create_visualizer() -> Dict[str, Any]:
    plt.rcParams["figure.figsize"] = (8, 6)

    x0_input = widgets.IntText(
        value=0, description="x0:", layout=widgets.Layout(width="150px"))
    y0_input = widgets.IntText(
        value=0, description="y0:", layout=widgets.Layout(width="150px"))
    x1_input = widgets.IntText(
        value=8, description="x1:", layout=widgets.Layout(width="150px"))
    y1_input = widgets.IntText(
        value=5, description="y1:", layout=widgets.Layout(width="150px"))
    apply_button = widgets.Button(
        description="Apply / Reset", button_style="primary", icon="refresh")
    prev_button = widgets.Button(description="Previous", icon="arrow-left")
    next_button = widgets.Button(
        description="Next", button_style="info", icon="arrow-right")
    complete_button = widgets.Button(
        description="Show complete line", icon="forward")
    step_slider = widgets.IntSlider(
        value=0,
        min=0,
        max=1,
        description="Step:",
        continuous_update=False,
        layout=widgets.Layout(width="620px"),
    )
    summary_output, plot_output, trace_output = (
        widgets.Output(),
        widgets.Output(),
        widgets.Output(),
    )
    state: Dict[str, List[Step]] = {"trace": []}

    def coordinates() -> Tuple[int, int, int, int]:
        return x0_input.value, y0_input.value, x1_input.value, y1_input.value

    def apply_coordinates(_=None) -> None:
        state["trace"] = bresenham_steps(*coordinates())
        step_slider.max = len(state["trace"]) - 1
        step_slider.value = 0
        render()

    def render(_=None) -> None:
        trace = state["trace"]
        if not trace:
            return
        k = min(step_slider.value, len(trace) - 1)
        s = trace[k]
        x0, y0, x1, y1 = coordinates()

        with summary_output:
            clear_output(wait=True)
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            print(f"Step {k} of {len(trace)-1}")
            print(f"Current: x={s.x}, y={s.y}")
            print(f"dx = {dx}, dy = {dy}, error = {s.error}")
            print(f"Correct x: {s.move_x} | Correct y: {s.move_y}")
            print(f"Decision: {s.note}")
            if s.next_x is not None:
                print(
                    f"Next: x={s.next_x}, y={s.next_y}, error = {s.next_error}")

        with plot_output:
            clear_output(wait=True)
            fig, ax = plt.subplots()
            all_x, all_y = [p.x for p in trace], [p.y for p in trace]
            visited = trace[: k + 1]
            ax.plot([x0, x1], [y0, y1], color="tab:blue",
                    linewidth=2, alpha=0.65, label="Ideal line")
            for px, py in zip(all_x, all_y):
                draw_cell(ax, px, py, facecolor="none",
                          edgecolor="0.75", linewidth=1.0, zorder=1)
            for p in visited:
                draw_cell(ax, p.x, p.y, facecolor="tab:orange",
                          edgecolor="black", alpha=0.85, linewidth=1.0, zorder=2)
            draw_cell(ax, s.x, s.y, facecolor="none",
                      edgecolor="red", linewidth=3.0, zorder=3)

            raster_legend = Rectangle(
                (0, 0), 1, 1, facecolor="none", edgecolor="0.75", label="Raster cells")
            selected_legend = Rectangle(
                (0, 0),
                1,
                1,
                facecolor="tab:orange",
                edgecolor="black",
                alpha=0.85,
                label="Selected pixels",
            )
            current_legend = Rectangle(
                (0, 0), 1, 1, facecolor="none", edgecolor="red", linewidth=3, label="Current pixel")
            if s.next_x is not None:
                ax.annotate("next", (s.next_x, s.next_y), xytext=(
                    8, 10), textcoords="offset points", color="darkred", weight="bold")
            pad = 1
            low_x, high_x = min(all_x + [x0, x1]) - \
                pad, max(all_x + [x0, x1]) + pad
            low_y, high_y = min(all_y + [y0, y1]) - \
                pad, max(all_y + [y0, y1]) + pad
            ax.set(
                xlim=(low_x - 0.5, high_x + 0.5),
                ylim=(low_y - 0.5, high_y + 0.5),
                xlabel="x",
                ylabel="y",
                title=f"Bresenham line: ({x0}, {y0}) to ({x1}, {y1})",
            )
            ax.set_xticks(range(low_x, high_x + 1))
            ax.set_yticks(range(low_y, high_y + 1))
            ax.set_xticks(
                [v - 0.5 for v in range(low_x, high_x + 2)], minor=True)
            ax.set_yticks(
                [v - 0.5 for v in range(low_y, high_y + 2)], minor=True)
            ax.grid(False, which="major")
            ax.grid(True, which="minor", color="0.85", linewidth=0.8)
            ax.set_aspect("equal", adjustable="box")
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(
                handles + [raster_legend, selected_legend, current_legend],
                labels + ["Raster cells", "Selected pixels", "Current pixel"],
                loc="best",
            )
            plt.show()

        with trace_output:
            clear_output(wait=True)
            print(
                f"{'i':>3} | {'x':>4} | {'y':>4} | {'dx':>4} | {'dy':>4} | {'error':>8} | {'move x':>6} | {'move y':>6}")
            print("-" * 62)
            for p in trace[: k + 1]:
                dx = abs(x1 - x0)
                dy = abs(y1 - y0)
                print(
                    f"{p.index:>3} | {p.x:>4} | {p.y:>4} | {dx:>4} | {dy:>4} | {p.error:>8.2f} | {str(p.move_x):>6} | {str(p.move_y):>6}")

        prev_button.disabled = k == 0
        next_button.disabled = k == len(trace) - 1

    apply_button.on_click(apply_coordinates)
    prev_button.on_click(lambda _: setattr(
        step_slider, "value", max(step_slider.min, step_slider.value - 1)))
    next_button.on_click(lambda _: setattr(
        step_slider, "value", min(step_slider.max, step_slider.value + 1)))
    complete_button.on_click(lambda _: setattr(
        step_slider, "value", step_slider.max))
    step_slider.observe(render, names="value")

    display(
        widgets.VBox(
            [
                widgets.HTML("<b>Line coordinates</b>"),
                widgets.HBox([x0_input, y0_input, x1_input, y1_input]),
                widgets.HBox([apply_button, prev_button,
                             next_button, complete_button]),
                step_slider,
            ]
        ),
        summary_output,
        plot_output,
        widgets.HTML("<b>Trace through current step</b>"),
        trace_output,
    )
    apply_coordinates()
    return {
        "x0_input": x0_input,
        "y0_input": y0_input,
        "x1_input": x1_input,
        "y1_input": y1_input,
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


__all__ = ["Step", "bresenham_steps", "draw_cell", "create_visualizer"]


if __name__ == "__main__":
    assert [(s.x, s.y) for s in bresenham_steps(0, 0, 5, 3)] == [
        (0, 0), (1, 1), (2, 1), (3, 2), (4, 2), (5, 3)]
    assert [(s.x, s.y) for s in bresenham_steps(2, 2, 2, 5)] == [
        (2, 2), (2, 3), (2, 4), (2, 5)]
    assert [(s.x, s.y) for s in bresenham_steps(3, 3, 0, 0)] == [
        (3, 3), (2, 2), (1, 1), (0, 0)]
    print("Algorithm checks passed.")
