from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import random
from IPython.display import clear_output, display
from matplotlib.patches import Circle, Rectangle


@dataclass
class Body:
    id: int
    x: float
    y: float
    vx: float
    vy: float
    radius: float


@dataclass(frozen=True)
class AABB:
    """Axis-aligned bounding box represented by center and half-extents."""
    cx: float
    cy: float
    half_w: float
    half_h: float

    def contains_point(self, x: float, y: float) -> bool:
        return (self.cx - self.half_w <= x <= self.cx + self.half_w and
                self.cy - self.half_h <= y <= self.cy + self.half_h)

    def intersects(self, other: "AABB") -> bool:
        return not (
            other.cx - other.half_w > self.cx + self.half_w or
            other.cx + other.half_w < self.cx - self.half_w or
            other.cy - other.half_h > self.cy + self.half_h or
            other.cy + other.half_h < self.cy - self.half_h
        )


class Quadtree:
    def __init__(self, boundary: AABB, capacity: int = 4, depth: int = 0,
                 max_depth: int = 7, events: Optional[List[tuple]] = None):
        self.boundary = boundary
        self.capacity = capacity
        self.depth = depth
        self.max_depth = max_depth
        self.events = events if events is not None else []
        self.points: List[Body] = []
        self.children: List[Quadtree] = []

    @property
    def divided(self) -> bool:
        return bool(self.children)

    def subdivide(self):
        b = self.boundary
        hw, hh = b.half_w / 2, b.half_h / 2
        self.events.append(("split", self))
        self.children = [
            Quadtree(AABB(b.cx - hw, b.cy - hh, hw, hh), self.capacity,
                     self.depth + 1, self.max_depth, self.events),
            Quadtree(AABB(b.cx + hw, b.cy - hh, hw, hh), self.capacity,
                     self.depth + 1, self.max_depth, self.events),
            Quadtree(AABB(b.cx - hw, b.cy + hh, hw, hh), self.capacity,
                     self.depth + 1, self.max_depth, self.events),
            Quadtree(AABB(b.cx + hw, b.cy + hh, hw, hh), self.capacity,
                     self.depth + 1, self.max_depth, self.events),
        ]

    def insert(self, body: Body) -> bool:
        if not self.boundary.contains_point(body.x, body.y):
            return False

        if len(self.points) < self.capacity or self.depth >= self.max_depth:
            self.points.append(body)
            self.events.append(("store", body, self))
            return True

        if not self.divided:
            self.subdivide()
            self.events.append((
                "retain", self, tuple(item.id for item in self.points)))

        for child in self.children:
            if child.boundary.contains_point(body.x, body.y):
                self.events.append(("handoff", body, self, child))
                return child.insert(body)
        return False

    def query(self, area: AABB, found=None, trace=None, query_body=None) -> List[Body]:
        if found is None:
            found = []
        if not self.boundary.intersects(area):
            if trace is not None:
                trace.append(("query_skip", query_body, self, area))
            return found

        if trace is not None:
            inside_ids = tuple(
                body.id for body in self.points
                if area.contains_point(body.x, body.y)
            )
            trace.append((
                "query_node",
                query_body,
                self,
                tuple(body.id for body in self.points),
                inside_ids,
            ))

        for body in self.points:
            if area.contains_point(body.x, body.y):
                found.append(body)
        for child in self.children:
            child.query(area, found, trace, query_body)
        return found

    def draw(self, ax, node_colors=None, node_labels=None):
        b = self.boundary
        node_color = node_colors.get(
            id(self), "0.55") if node_colors else "0.55"
        ax.add_patch(Rectangle(
            (b.cx - b.half_w, b.cy - b.half_h),
            2 * b.half_w, 2 * b.half_h,
            facecolor="none", edgecolor=node_color,
            linewidth=1.5, alpha=0.85
        ))
        if node_labels:
            ax.text(
                b.cx - b.half_w + 0.8,
                b.cy + b.half_h - 1.5,
                node_labels[id(self)],
                ha="left",
                va="top",
                fontsize=7,
                color="#304050",
                fontweight="bold",
            )
        for child in self.children:
            child.draw(ax, node_colors, node_labels)

    def count_nodes(self) -> int:
        return 1 + sum(child.count_nodes() for child in self.children)

    def iter_nodes(self):
        yield self
        for child in self.children:
            yield from child.iter_nodes()

    def draw_contents(self, ax, node_labels):
        nodes = list(self.iter_nodes())
        deepest = max((node.depth for node in nodes), default=0)
        for node in nodes:
            boundary = node.boundary
            depth_color = plt.cm.viridis(
                node.depth / deepest if deepest else 0.0)
            object_ids = ", ".join(
                str(body.id) for body in node.points) or "empty"
            ax.add_patch(Rectangle(
                (boundary.cx - boundary.half_w,
                 boundary.cy - boundary.half_h),
                2 * boundary.half_w,
                2 * boundary.half_h,
                facecolor=depth_color,
                edgecolor=depth_color,
                linewidth=1.2,
                alpha=0.12,
            ))
            ax.text(
                boundary.cx,
                boundary.cy,
                f"{node_labels[id(node)]}\n"
                f"depth {node.depth}\n"
                f"[{object_ids}]",
                ha="center",
                va="center",
                fontsize=7,
                color="#304050",
            )

    def draw_structure(self, ax, node_colors, node_labels):
        positions = {}
        next_row = [0]

        def assign_position(node):
            child_rows = [assign_position(child) for child in node.children]
            if child_rows:
                row = sum(child_rows) / len(child_rows)
            else:
                row = next_row[0]
                next_row[0] += 1
            positions[id(node)] = (node.depth, row)
            return row

        assign_position(self)
        nodes = list(self.iter_nodes())
        for node in nodes:
            x, y = positions[id(node)]
            for child in node.children:
                child_x, child_y = positions[id(child)]
                ax.plot([x, child_x], [y, child_y], color="#8a969e",
                        linewidth=1.0, zorder=1)

        for node in nodes:
            x, y = positions[id(node)]
            boundary = node.boundary
            object_ids = ", ".join(
                str(body.id) for body in node.points) or "empty"
            ax.text(
                x,
                y,
                f"{node_labels[id(node)]}\n"
                f"depth {node.depth}\n"
                f"x=[{boundary.cx - boundary.half_w:.1f}, "
                f"{boundary.cx + boundary.half_w:.1f}]\n"
                f"y=[{boundary.cy - boundary.half_h:.1f}, "
                f"{boundary.cy + boundary.half_h:.1f}]\n"
                f"objects: [{object_ids}]",
                ha="center",
                va="center",
                fontsize=7,
                color="#263238",
                bbox={
                    "boxstyle": "round,pad=0.35",
                    "facecolor": node_colors[id(node)],
                    "edgecolor": "#263238",
                    "linewidth": 0.9,
                    "alpha": 0.95,
                },
                zorder=2,
            )

        deepest = max((node.depth for node in nodes), default=0)
        ax.set_xlim(-0.6, deepest + 0.6)
        ax.set_ylim(-1, max(next_row[0], 1))
        ax.invert_yaxis()
        ax.set_xticks(range(deepest + 1))
        ax.set_xlabel("Tree depth (root = 0)")
        ax.set_ylabel("")
        ax.set_yticks([])
        ax.grid(axis="x", alpha=0.2)

    def node_colors(self):
        pastel_colors = (
            "#b9dcff", "#fff1b8", "#c9edc9", "#c8d8ff",
            "#ffe4b8", "#bfe8df", "#d7c9ff", "#f5d0b5",
            "#c9f0e8", "#e4d6ff", "#f6e5b8", "#cfe7d0",
        )
        colors = {}
        for index, node in enumerate(self.iter_nodes()):
            colors[id(node)] = pastel_colors[index % len(pastel_colors)]
        return colors

    def body_colors(self, node_colors):
        colors = {}
        for node in self.iter_nodes():
            for body in node.points:
                colors[body.id] = node_colors[id(node)]
        return colors

    def node_labels(self):
        return {
            id(node): f"N{index}"
            for index, node in enumerate(self.iter_nodes())
        }


def circles_collide(a: Body, b: Body) -> bool:
    dx, dy = a.x - b.x, a.y - b.y
    limit = a.radius + b.radius
    return dx * dx + dy * dy <= limit * limit


WORLD_W, WORLD_H = 100.0, 70.0


def create_bodies(count: int, seed: int, speed: float) -> List[Body]:
    rng = random.Random(seed)
    radius_choices = (1.2, 1.8, 2.6, 3.8, 5.2)
    bodies = []
    for i in range(count):
        radius = rng.choice(radius_choices)
        angle = rng.uniform(0, 2 * np.pi)
        magnitude = rng.uniform(0.45, 1.0) * speed
        bodies.append(Body(
            id=i,
            x=rng.uniform(radius, WORLD_W - radius),
            y=rng.uniform(radius, WORLD_H - radius),
            vx=np.cos(angle) * magnitude,
            vy=np.sin(angle) * magnitude,
            radius=radius,
        ))
    return bodies


def move_bodies(bodies: List[Body], dt: float):
    for body in bodies:
        body.x += body.vx * dt
        body.y += body.vy * dt

        if body.x - body.radius < 0:
            body.x = body.radius
            body.vx = abs(body.vx)
        elif body.x + body.radius > WORLD_W:
            body.x = WORLD_W - body.radius
            body.vx = -abs(body.vx)

        if body.y - body.radius < 0:
            body.y = body.radius
            body.vy = abs(body.vy)
        elif body.y + body.radius > WORLD_H:
            body.y = WORLD_H - body.radius
            body.vy = -abs(body.vy)


def build_tree(bodies: List[Body], capacity: int) -> Quadtree:
    events = []
    tree = Quadtree(
        AABB(WORLD_W / 2, WORLD_H / 2, WORLD_W / 2, WORLD_H / 2),
        capacity=capacity,
        events=events,
    )
    for body in bodies:
        tree.insert(body)
    return tree


def detect_collisions(bodies: List[Body], tree: Quadtree):
    max_radius = max((body.radius for body in bodies), default=0)
    candidate_pairs: Set[Tuple[int, int]] = set()

    for body in bodies:
        reach = body.radius + max_radius
        query_area = AABB(body.x, body.y, reach, reach)
        tree.events.append(("query_start", body, query_area, max_radius))
        nearby = tree.query(
            query_area,
            trace=tree.events,
            query_body=body,
        )
        tree.events.append((
            "query_result",
            body,
            tuple(sorted(other.id for other in nearby if other.id != body.id)),
        ))
        for other in nearby:
            if other.id != body.id:
                candidate_pairs.add(tuple(sorted((body.id, other.id))))

    by_id = {body.id: body for body in bodies}
    collision_pairs = {
        pair for pair in candidate_pairs
        if circles_collide(by_id[pair[0]], by_id[pair[1]])
    }
    for pair in sorted(candidate_pairs):
        tree.events.append((
            "collision_check", pair, pair in collision_pairs))
    colliding_ids = {item for pair in collision_pairs for item in pair}
    return candidate_pairs, collision_pairs, colliding_ids


def create_visualizer():
    plt.rcParams["figure.figsize"] = (9, 7)

    count_input = widgets.IntSlider(
        value=35, min=5, max=100, step=5, description="Objects:",
        continuous_update=False)
    capacity_input = widgets.IntSlider(
        value=4, min=1, max=10, description="Node capacity:",
        continuous_update=False)
    seed_input = widgets.IntText(value=7, description="Seed:")
    speed_input = widgets.FloatSlider(
        value=8.0, min=1.0, max=20.0, step=1.0, description="Speed:",
        continuous_update=False)
    dt_input = widgets.FloatSlider(
        value=0.12, min=0.03, max=0.4, step=0.01, description="Step size:",
        continuous_update=False)
    show_candidates = widgets.Checkbox(
        value=True, description="Show candidate collision checks")

    reset_button = widgets.Button(
        description="Reset", icon="refresh", button_style="primary")
    step_button = widgets.Button(
        description="Step", icon="step-forward", button_style="info")
    play = widgets.Play(
        value=0, min=0, max=100000, step=1, interval=120, description="Play")
    frame_slider = widgets.IntSlider(
        value=0, min=0, max=100000, step=1, description="Frame:",
        continuous_update=True)
    widgets.jslink((play, "value"), (frame_slider, "value"))

    plot_output = widgets.Output()
    stats_output = widgets.Output()
    tree_graph_output = widgets.Output()
    tree_structure_output = widgets.Output()
    tree_contents_output = widgets.Output(
        layout=widgets.Layout(max_height="320px", overflow="auto"))
    event_output = widgets.Output(
        layout=widgets.Layout(max_height="420px", overflow="auto"))
    state = {"bodies": [], "frame": 0, "last_widget_frame": 0}

    def reset(_=None):
        state["bodies"] = create_bodies(
            count_input.value, seed_input.value, speed_input.value)
        state["frame"] = 0
        state["last_widget_frame"] = frame_slider.value
        render_scene()

    def advance(steps=1):
        for _ in range(max(0, steps)):
            move_bodies(state["bodies"], dt_input.value)
            state["frame"] += 1
        render_scene()

    def step_once(_=None):
        advance(1)

    def animation_changed(change):
        delta = change["new"] - state["last_widget_frame"]
        state["last_widget_frame"] = change["new"]
        if delta > 0:
            advance(delta)

    def render_scene(_=None):
        bodies = state["bodies"]
        if not bodies:
            return

        tree = build_tree(bodies, capacity_input.value)
        candidates, collisions, colliding_ids = detect_collisions(bodies, tree)
        node_colors = tree.node_colors()
        body_colors = tree.body_colors(node_colors)
        node_labels = tree.node_labels()
        by_id = {body.id: body for body in bodies}
        naive_checks = len(bodies) * (len(bodies) - 1) // 2
        avoided = naive_checks - len(candidates)
        reduction = 100 * avoided / naive_checks if naive_checks else 0

        with plot_output:
            clear_output(wait=True)
            fig, ax = plt.subplots()
            tree.draw(ax, node_colors, node_labels)

            if show_candidates.value:
                for a_id, b_id in candidates:
                    if (a_id, b_id) not in collisions:
                        a, b = by_id[a_id], by_id[b_id]
                        ax.plot(
                            [a.x, b.x], [a.y, b.y], color="#005f73",
                            alpha=0.8, linewidth=1.2, linestyle="--",
                        )

            for a_id, b_id in collisions:
                a, b = by_id[a_id], by_id[b_id]
                ax.plot([a.x, b.x], [a.y, b.y], color="crimson",
                        alpha=0.8, linewidth=1.5)

            for body in bodies:
                fill_color = "crimson" if body.id in colliding_ids else body_colors[body.id]
                ax.add_patch(Circle(
                    (body.x, body.y), body.radius, facecolor=fill_color,
                    edgecolor="#263238", linewidth=1.8, alpha=0.7))
                ax.text(
                    body.x,
                    body.y,
                    str(body.id),
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="black" if body.id not in colliding_ids else "white",
                    fontweight="bold",
                )

            ax.set_xlim(0, WORLD_W)
            ax.set_ylim(0, WORLD_H)
            ax.set_aspect("equal", adjustable="box")
            ax.set_title(
                f"Quadtree Collision Detection | Frame {state['frame']}")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(False)
            plt.show()

        with stats_output:
            clear_output(wait=True)
            print(f"Objects: {len(bodies)}")
            print(f"Quadtree nodes: {tree.count_nodes()}")
            print(f"Candidate checks: {len(candidates)}")
            print(f"Naive all-pairs checks: {naive_checks}")
            print(f"Checks avoided this frame: {avoided} ({reduction:.1f}%)")
            print(f"Collision pairs: {len(collisions)}")

        with tree_graph_output:
            clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(10, 7))
            tree.draw_contents(ax, node_labels)
            ax.set_xlim(0, WORLD_W)
            ax.set_ylim(0, WORLD_H)
            ax.set_aspect("equal", adjustable="box")
            ax.set_title(
                f"Quadtree Elements and Contents | Frame {state['frame']}"
            )
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(False)
            plt.show()

        with tree_structure_output:
            clear_output(wait=True)
            fig, ax = plt.subplots(figsize=(11, 7))
            tree.draw_structure(ax, node_colors, node_labels)
            ax.set_title(
                f"Quadtree Structure by Depth | Frame {state['frame']}"
            )
            plt.show()

        with tree_contents_output:
            clear_output(wait=True)
            print("Legend: N# = quadtree region; object numbers = circle IDs.")
            print(
                "Structure: a node splits after it reaches its capacity "
                f"of {capacity_input.value} stored objects."
            )
            print(
                "The existing objects stay in the parent; later objects "
                "are inserted into matching child nodes."
            )
            print(
                "Splitting stops at the maximum depth "
                f"({tree.max_depth})."
            )
            print(f"Quadtree elements and contents | Frame {state['frame']}")
            for index, node in enumerate(tree.iter_nodes()):
                boundary = node.boundary
                object_ids = ", ".join(
                    str(body.id) for body in node.points) or "empty"
                state_label = "split" if node.divided else "leaf"
                print(
                    f"N{index:02d}  depth={node.depth}  {state_label}  "
                    f"stored={len(node.points)}/{node.capacity}  "
                    f"center=({boundary.cx:.1f}, {boundary.cy:.1f})  "
                    f"size=({2 * boundary.half_w:.1f} x "
                    f"{2 * boundary.half_h:.1f})  "
                    f"objects=[{object_ids}]"
                )

        with event_output:
            clear_output(wait=True)
            print(f"What happened this frame? | Frame {state['frame']}")
            for event in tree.events:
                event_type = event[0]
                if event_type == "split":
                    node = event[1]
                    print(
                        f"SPLIT {node_labels[id(node)]}: stored "
                        f"{len(node.points)}/{node.capacity}; created 4 children"
                    )
                elif event_type == "retain":
                    node, object_ids = event[1], event[2]
                    retained = ", ".join(str(item) for item in object_ids)
                    print(
                        f"RETAIN {node_labels[id(node)]}: existing objects "
                        f"[{retained}] stay in the parent"
                    )
                elif event_type == "handoff":
                    body, parent, child = event[1], event[2], event[3]
                    print(
                        f"HANDOFF object {body.id}: "
                        f"{node_labels[id(parent)]} -> {node_labels[id(child)]}"
                    )
                elif event_type == "store":
                    body, node = event[1], event[2]
                    print(
                        f"STORE object {body.id}: "
                        f"placed in {node_labels[id(node)]} "
                        f"(depth {node.depth})"
                    )
                elif event_type == "query_start":
                    body, area, max_radius = event[1], event[2], event[3]
                    print(
                        f"QUERY START object {body.id}: center="
                        f"({area.cx:.1f}, {area.cy:.1f}), "
                        f"half-size=({area.half_w:.1f}, {area.half_h:.1f}) "
                        f"= object radius {body.radius:.1f} + "
                        f"largest radius {max_radius:.1f}"
                    )
                elif event_type == "query_node":
                    body, node = event[1], event[2]
                    stored_ids, inside_ids = event[3], event[4]
                    stored = ", ".join(str(item) for item in stored_ids)
                    inside = ", ".join(str(item) for item in inside_ids)
                    print(
                        f"VISIT object {body.id}: "
                        f"{node_labels[id(node)]} depth={node.depth}, "
                        f"stored=[{stored or 'empty'}] -> "
                        f"candidates=[{inside or 'none'}]"
                    )
                elif event_type == "query_skip":
                    body, node, area = event[1], event[2], event[3]
                    boundary = node.boundary
                    node_x = (boundary.cx - boundary.half_w,
                              boundary.cx + boundary.half_w)
                    node_y = (boundary.cy - boundary.half_h,
                              boundary.cy + boundary.half_h)
                    area_x = (area.cx - area.half_w, area.cx + area.half_w)
                    area_y = (area.cy - area.half_h, area.cy + area.half_h)
                    print(
                        f"SKIP object {body.id}: "
                        f"{node_labels[id(node)]} depth={node.depth} "
                        f"bounds x=[{node_x[0]:.1f}, {node_x[1]:.1f}], "
                        f"y=[{node_y[0]:.1f}, {node_y[1]:.1f}] do not overlap "
                        f"search x=[{area_x[0]:.1f}, {area_x[1]:.1f}], "
                        f"y=[{area_y[0]:.1f}, {area_y[1]:.1f}]; "
                        "entire branch skipped"
                    )
                elif event_type == "query_result":
                    body, object_ids = event[1], event[2]
                    candidates = ", ".join(str(item) for item in object_ids)
                    print(
                        f"QUERY object {body.id}: candidate objects "
                        f"[{candidates or 'none'}]"
                    )
                elif event_type == "collision_check":
                    pair, collided = event[1], event[2]
                    result = "INTERSECTION" if collided else "no intersection"
                    print(
                        f"CHECK objects {pair[0]} and {pair[1]}: {result}"
                    )

    reset_button.on_click(reset)
    step_button.on_click(step_once)
    frame_slider.observe(animation_changed, names="value")
    show_candidates.observe(render_scene, names="value")
    capacity_input.observe(render_scene, names="value")

    controls = widgets.VBox([
        widgets.HBox([count_input, capacity_input, seed_input]),
        widgets.HBox([speed_input, dt_input, show_candidates]),
        widgets.HBox([reset_button, step_button, play]),
    ])

    display(
        controls,
        stats_output,
        plot_output,
        tree_graph_output,
        tree_structure_output,
        tree_contents_output,
        event_output,
    )
    reset()
