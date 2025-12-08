from db_to_dict import get_data
import plotly.graph_objects as go

df = get_data("db.sqlite")

times = df["timestamp"].dropna().sort_values().unique()

frames = []
for t in times:
    d = df[df["timestamp"] == t]
    values = d["value"].astype(float)
    v_min = values.min()

    frames.append(
        go.Frame(
            data=[
                go.Scatter(
                    x=d["x"],
                    y=d["y"],
                    mode="markers+text",
                    text=d["name"],
                    textposition="top center",
                    marker=dict(
                        size=(values - v_min + 1) * 5,
                        color=values,
                        colorbar=dict(title="value"),
                        showscale=True,
                    ),
                )
            ],
            name=str(t)
        )
    )

# initial frame
d0 = df[df["timestamp"] == times[0]]
values0 = d0["value"].astype(float)
v0_min = values0.min()

fig = go.Figure(
    data=[
        go.Scatter(
            x=d0["x"],
            y=d0["y"],
            mode="markers+text",
            text=d0["name"],
            textposition="top center",
            marker=dict(
                size=(values0 - v0_min + 1) * 5,
                color=values0,
                colorbar=dict(title="value"),
                showscale=True,
            ),
        )
    ],
    layout=go.Layout(
        xaxis=dict(title="x"),
        yaxis=dict(title="y"),
        title="Fruit values over time in 2D space",
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 300, "redraw": True},
                                     "fromcurrent": True}]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate"}]
                    )
                ]
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[[str(t)], {"frame": {"duration": 0, "redraw": True},
                                         "mode": "immediate"}],
                        label=str(t)
                    )
                    for t in times
                ],
                currentvalue={"prefix": "Time: "}
            )
        ]
    ),
    frames=frames
)

fig.show()
