import argparse
from pathlib import Path

import bokeh.plotting as bkp
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore

import esparto as es

lorem = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore "
    "magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo "
    "consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
)

image_path = Path("docs/examples/my-image.png")
image = es.Image(str(image_path), caption="Photo by Benjamin Voros on Unsplash")

df = pd.DataFrame()
df["A"] = np.random.normal(10, 4, 1000)
df["B"] = np.random.normal(-10, 6, 1000)
df["C"] = np.random.normal(0, 3, 1000)
df["D"] = np.random.normal(-5, 8, 1000)
df = df.round(3)


def example_01(pdf: bool = False):
    page = es.Page(title="Columns Page", navbrand="esparto", table_of_contents=2)

    page["Section One"]["Row One"]["Column One"] = lorem
    page["Section Two"] = es.Section()
    page["Section Three"] = es.CardSection()
    page["Section Four"] = es.Section()
    page["Section Five"] = es.CardSection()

    for i in range(1, 5):
        page["Section Two"][f"Row {i}"] = [(image, lorem) for _ in range(1, i + 1)]
        page["Section Three"][f"Row {i}"] += [
            lorem if j % 2 == 0 else {"Card Title": image} for j in range(1, i + 1)
        ]
        page["Section Four"][f"Row {i}"] += [
            {"Column Title": lorem} for _ in range(1, i + 1)
        ]
        page["Section Five"][f"Row {i}"] += [
            {"Card Title": lorem} for _ in range(1, i + 1)
        ]

    page.save_html("page01.html")

    if pdf:
        page.save_pdf("page01.pdf")


def example_02(pdf: bool = False):
    page = es.Page(title="Matplotlib Page")

    _ = df.plot.hist(alpha=0.4, bins=30)
    fig = plt.gcf()
    fig.tight_layout()

    _ = df.plot.hist(alpha=0.4, bins=30)
    fig2 = plt.gcf()
    fig2.tight_layout()
    fig2.set_size_inches(4, 3)

    page[0][0] = df[:10], fig
    page[0][1] = ({"fig": fig}, {"table": df[:10]})
    page[0][2] = es.CardRowEqual(children=[{"fig": fig}, {"table": df[:10]}][::-1])
    page[0][3] = {"text": lorem}, {"table": df[:10]}
    page[0][4] = fig
    page[0][5] = fig2

    page.save_html("page02-mpl.html")

    if pdf:
        page.save_pdf("page02-mpl.pdf")


def example_03(pdf: bool = False):
    page = es.Page(title="Markdown Page", max_width=600)
    page += "tests/resources/markdown.md"
    page.save_html("page03-markdown.html")

    if pdf:
        page.save_pdf("page03-markdown.pdf")


def example_04(pdf: bool = False):
    page = es.Page(title="Plotly Page")

    fig = px.scatter(data_frame=df, x="A", y="B")
    fig2 = px.scatter(data_frame=df, x="A", y="B", width=400, height=300)

    page[0][0] = df[:10], fig
    page[0][1] = ({"fig": fig}, {"table": df[:10]})
    page[0][2] = es.CardRowEqual(children=[{"fig": fig}, {"table": df[:10]}][::-1])
    page[0][3] = {"text": lorem}, {"table": df[:10]}
    page[0][4] = ({"fig": fig}, {"fig": fig})
    page[0][5] = fig
    page[0][6] = fig2

    page.save_html("page04-plotly.html")

    if pdf:
        page.save_pdf("page04-plotly.pdf")


def example_05(pdf: bool = False):
    page = es.Page(
        title="Slim Page",
        navbrand="esparto",
        table_of_contents=2,
        body_styles={"max-width": "700px"},
    )

    page["Section One"]["Row One"]["Column One"] = lorem
    page["Section Two"] = es.Section()
    page["Section Three"] = es.CardSection()
    page["Section Four"] = es.Section()
    page["Section Five"] = es.CardSection()

    for i in range(1, 5):
        page["Section Two"][f"Row {i}"] = [(image, lorem) for _ in range(1, i + 1)]
        page["Section Three"][f"Row {i}"] += [
            lorem if j % 2 == 0 else {"Card Title": image} for j in range(1, i + 1)
        ]
        page["Section Four"][f"Row {i}"] += [
            {"Column Title": lorem} for _ in range(1, i + 1)
        ]
        page["Section Five"][f"Row {i}"] += [
            {"Card Title": lorem} for _ in range(1, i + 1)
        ]

    page.save_html("page05.html")

    if pdf:
        page.save_pdf("page05.pdf")


def example_06(pdf: bool = False):
    page = es.Page(title="Bokeh Page")

    fig = bkp.figure(title="One")
    fig.circle("A", "B", source=df)

    page[0][0] = df[:10], fig
    page[0][1] = ({"fig": fig}, {"table": df[:10]})
    page[0][2] = es.CardRowEqual(children=[{"fig": fig}, {"table": df[:10]}][::-1])
    page[0][3] = {"text": lorem}, {"table": df[:10]}
    page[0][4] = ({"fig": fig}, {"fig": fig})

    fig2 = bkp.figure(title="Two", width=400, height=300)
    fig2.circle("A", "B", source=df)
    page[0][5] = fig2

    page.save_html("page06-bokeh.html")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", action="store_true")

    args = parser.parse_args()

    pdf = args.pdf

    print("Producing example output...", end="", flush=True)

    example_01(pdf)
    example_02(pdf)
    example_03(pdf)
    example_04(pdf)
    example_05(pdf)
    example_06(pdf)

    print("Done.")


if __name__ == "__main__":
    main()
