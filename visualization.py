import networkx as nx
import plotly.graph_objects as go
from typing import List, Tuple

class AgentVisualizer:
    """Utility to visualize agent interactions using Plotly."""

    def __init__(self) -> None:
        # Predefined nodes and layout for the agent graph
        self.nodes = ["CEO", "Worker", "QA", "Reflection", "END"]
        self.pos = {
            "CEO": (0, 1),
            "Worker": (-1, 0),
            "QA": (1, 0),
            "Reflection": (0, -1),
            "END": (0, -2),
        }
        self.edges = [
            ("CEO", "Worker"),
            ("CEO", "QA"),
            ("CEO", "Reflection"),
            ("CEO", "END"),
            ("Worker", "Reflection"),
            ("QA", "Reflection"),
            ("Reflection", "CEO"),
        ]
        self.animation_frames = [self.create_animation_frame([])]

    def create_animation_frame(self, highlight: List[Tuple[str, str]]):
        """Create a Plotly figure representing the agent graph.

        Parameters
        ----------
        highlight: list of edges that should be emphasized in this frame.
        """
        G = nx.DiGraph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from(self.edges)

        edge_x = []
        edge_y = []
        edge_colors = []
        for u, v in self.edges:
            x0, y0 = self.pos[u]
            x1, y1 = self.pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            color = "red" if (u, v) in highlight else "gray"
            edge_colors.append(color)

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=2, color="gray"),
            hoverinfo="none",
            mode="lines",
        )

        node_x = [self.pos[n][0] for n in self.nodes]
        node_y = [self.pos[n][1] for n in self.nodes]
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=self.nodes,
            textposition="bottom center",
            marker=dict(size=20, color="lightblue", line=dict(width=2, color="black")),
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        # Highlight selected edges by adding them on top with a different color
        if highlight:
            hx = []
            hy = []
            for u, v in highlight:
                x0, y0 = self.pos[u]
                x1, y1 = self.pos[v]
                hx += [x0, x1, None]
                hy += [y0, y1, None]
            fig.add_trace(
                go.Scatter(
                    x=hx,
                    y=hy,
                    line=dict(width=4, color="red"),
                    hoverinfo="none",
                    mode="lines",
                )
            )
        fig.update_layout(
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            margin=dict(l=20, r=20, t=20, b=20),
        )
        return fig

    def animate_flow(self, flow: List[List[Tuple[str, str]]]):
        """Create animation frames for a sequence of edge transitions."""
        frames = [self.create_animation_frame([])]
        for step in flow:
            frames.append(self.create_animation_frame(step))
        self.animation_frames = frames
