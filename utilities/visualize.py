import math

import numpy as np
import plotly.graph_objects as go
from plotly.colors import sequential
from stl.mesh import Mesh

from extrema import find_extrema


def get_stl(stl_file):
    """
    Taken from https://community.plotly.com/t/view-3d-cad-data/16920/9
    """
    stl_mesh = Mesh.from_file(stl_file)
    return stl_mesh


def visualize_disc(stl_mesh, nose, roll):
    """
    Taken from https://community.plotly.com/t/view-3d-cad-data/16920/9
    """
    stl_mesh.rotate([1, 0, 0], math.radians(-1*nose))
    stl_mesh.rotate([0, 1, 0], math.radians(roll))
    # stl_mesh.rotate([0, 0, 1], math.radians(z_angle))

    p, q, r = stl_mesh.vectors.shape  # (p, 3, 3)
    # the array stl_mesh.vectors.reshape(p*q, r) can contain multiple copies of the same vertex;
    # extract unique vertices from all mesh triangles
    vertices, ixr = np.unique(stl_mesh.vectors.reshape(p * q, r), return_inverse=True, axis=0)
    I = np.take(ixr, [3 * k for k in range(p)])
    J = np.take(ixr, [3 * k + 1 for k in range(p)])
    K = np.take(ixr, [3 * k + 2 for k in range(p)])

    x, y, z = vertices.T
    trace = go.Mesh3d(x=x, y=y, z=z, i=I, j=J, k=K)
    # optional parameters to make it look nicer
    trace.update(flatshading=True, lighting_facenormalsepsilon=0, lighting_ambient=0.7)

    fig = go.Figure(trace)

    # Add camera controls to the plot
    camera = dict(
            eye=dict(x=0, y=-3, z=0)
            )
    fig.update_layout(scene_camera=camera)

    fig.update_layout(
            scene=dict(
                    xaxis=dict(nticks=4, range=[-0.11, 0.11], ),
                    yaxis=dict(nticks=4, range=[-0.11, 0.11], ),
                    zaxis=dict(nticks=4, range=[-0.11, 0.11], ), )
            )
    return fig


import plotly.subplots as sp


def get_plot(x, y, z):
    xm = np.min(x) - 1.5
    xM = np.max(x) + 1.5
    ym = -5
    yM = np.max(y) + 1.5
    zm = np.min(z)
    zM = np.max(z)
    N = len(x)
    category = 'Height'
    x_extrema, y_extrema, extrema_type = find_extrema(x, y)

    xM_abs = max(abs(xm), abs(xM))
    xm_abs = -1 * xM_abs

    carats_v = go.Scatter(
            x=[category, category],
            y=[min(z), max(z)],
            mode='markers',
            showlegend=False,
            marker=dict(symbol=['arrow-up', 'arrow-down'], size=20, color=['red', 'red']),
            name='Carets',
            )
    carats_h = go.Scatter(
            x=[min(x), max(x)],
            y=['', ''],
            mode='markers',
            showlegend=False,
            marker=dict(symbol=['arrow-right', 'arrow-left'], size=20, color=['red', 'red']),
            name='Carets',
            )

    extrema = go.Scatter(
            x=x_extrema,
            y=y_extrema,
            mode='markers',
            showlegend=False,
            marker=dict(symbol=extrema_type, size=20, color='blue'),
            name='Extrema',
            )

    # Create figure with subplots
    fig = sp.make_subplots(rows=2, cols=2, subplot_titles=("Flight Path", "Height", "Lateral Deviance"),
                           specs=[[{"rowspan": 2}, {}], [None, {}]], row_heights=[0.5, 0.5])

    # Add traces to the main plot
    fig.add_trace(
            go.Scatter(x=x, y=y,
                       mode="lines",
                       showlegend=False,
                       line=dict(width=1, color='black')),
            row=1, col=1
            )

    fig.add_trace(
            go.Scatter(x=x, y=y,
                       showlegend=False,
                       mode="markers", marker_colorscale=sequential.Peach,
                       marker=dict(color=z, size=3, showscale=True)),
            row=1, col=1
            )

    fig.add_trace(
            extrema,
            row=1, col=1
            )

    # Add trace for the subplot
    fig.add_trace(carats_v,
                  row=1, col=2
                  )
    fig.add_trace(
            go.Bar(
                    x=[],
                    y=[],
                    showlegend=False,
                    ),
            row=1, col=2
            )
    # Add trace for the subplot
    fig.add_trace(carats_h,
                  row=2, col=2
                  )
    fig.add_trace(
            go.Bar(
                    x=[],
                    y=[],
                    showlegend=False,
                    orientation='h',
                    ),
            row=2, col=2
            )

    # Update layout
    fig.update_layout(
            xaxis=dict(range=[xm, xM], autorange=False, zeroline=False),
            yaxis=dict(range=[ym, yM], autorange=False, zeroline=False),
            title_text="Flight Path",
            hovermode="closest",
            updatemenus=[
                dict(
                        type="buttons",
                        buttons=[
                            dict(
                                    label="Play",
                                    method="animate",
                                    args=[None, {"frame": {"duration": 30, "redraw": True}, "fromcurrent": True}]
                                    ),
                            dict(
                                    label="Pause",
                                    method="animate",
                                    args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate",
                                                   "transition": {"duration": 0}}]
                                    )
                            ],
                        showactive=False,
                        x=0.05,
                        y=0.05
                        )
                ],
            )

    # Create frames for the main plot and subplot
    all_frames = [
        go.Frame(data=[
            go.Scatter(
                    x=[x[k]],
                    y=[y[k]],
                    mode="markers",
                    showlegend=False,
                    marker=dict(color="red", size=10)),
            go.Scatter(x=x, y=y,
                       mode="markers", marker_colorscale=sequential.Peach,
                       marker=dict(color=z, size=3, showscale=True)),
            extrema,
            carats_v,
            go.Bar(
                    x=['Height'],
                    y=[z[k]],
                    showlegend=False,
                    name='Value',
                    marker=dict(color='orange', line=dict(width=1))
                    # Set color of value bar to orange and line width to 1
                    ),
            carats_h,
            go.Bar(
                    x=[x[k]],
                    y=[''],
                    showlegend=False,
                    name='Value',
                    orientation='h',
                    marker=dict(color='orange', line=dict(width=1))
                    # Set color of value bar to orange and line width to 1
                    )
            ])
        for k in range(N)
        ]

    # Combine frames for the main plot and subplot
    fig.frames = all_frames
    fig.update_yaxes(scaleanchor="x", scaleratio=1, row=1, col=1)
    fig.update_yaxes(range=[zm - 2, zM + 2], fixedrange=True, row=1, col=2)
    fig.update_xaxes(range=[xm_abs, xM_abs], fixedrange=True, row=2, col=2)

    # # Add green rectangle at the bottom of the plot
    fig.update_layout(
            shapes=[dict(type="rect", xref="x", yref="y",
                         x0=-1, y0=0, x1=1, y1=-4, fillcolor="gray",
                         opacity=1, layer="below")],
            plot_bgcolor="green",
            )

    return fig


import plotly.graph_objs as go
from plotly.subplots import make_subplots


def get_subplots(arc, alphas, lifts, drags, moms, rolls, velocity):
    fig = make_subplots(rows=2, cols=3, specs=[[{}, {}, {}], [{}, {}, {}]],
                        subplot_titles=("Lift force (N)", "Drag force (N)", "Moment (Nm)",
                                        "Angle of attack (deg)", "Velocities (m/s)", "Roll rate (rad/s)"),
                        shared_xaxes=True)

    fig.add_trace(go.Scatter(x=arc, y=lifts, name="Lift force (N)"), row=1, col=1)
    fig.update_xaxes(title_text="Distance (m)", row=1, col=1)
    fig.update_yaxes(title_text="Lift force (N)", row=1, col=1)

    fig.add_trace(go.Scatter(x=arc, y=drags, name="Drag force (N)"), row=1, col=2)
    fig.update_xaxes(title_text="Distance (m)", row=1, col=2)
    fig.update_yaxes(title_text="Drag force (N)", row=1, col=2)

    fig.add_trace(go.Scatter(x=arc, y=moms, name="Moment (Nm)"), row=1, col=3)
    fig.update_xaxes(title_text="Distance (m)", row=1, col=3)
    fig.update_yaxes(title_text="Moment (Nm)", row=1, col=3)

    fig.add_trace(go.Scatter(x=arc, y=alphas, name="Angle of attack (deg)"), row=2, col=1)
    fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
    fig.update_yaxes(title_text="Angle of attack (deg)", row=2, col=1)

    fig.add_trace(go.Scatter(x=arc, y=velocity[0, :], name="u"), row=2, col=2)
    fig.add_trace(go.Scatter(x=arc, y=velocity[1, :], name="v"), row=2, col=2)
    fig.add_trace(go.Scatter(x=arc, y=velocity[2, :], name="w"), row=2, col=2)
    fig.update_xaxes(title_text="Distance (m)", row=2, col=2)
    fig.update_yaxes(title_text="Velocities (m/s)", row=2, col=2)
    fig.update_traces(mode='lines', row=2, col=2)

    fig.add_trace(go.Scatter(x=arc, y=rolls, name="Roll rate (rad/s)"), row=2, col=3)
    fig.update_xaxes(title_text="Distance (m)", row=2, col=3)
    fig.update_yaxes(title_text="Roll rate (rad/s)", row=2, col=3)

    fig.update_layout(height=600, width=1000, title_text="Plotly Subplots", hovermode='x')
    return fig
