from pathlib import Path

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

df = df


def example_01():
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
    page.save_pdf("page01.pdf")


def example_02():
    page = es.Page(title="Matplotlib Page")

    _ = df.plot.hist(alpha=0.4, bins=30)
    fig = plt.gcf()
    fig.tight_layout()

    page[0][0] = df[:10], fig

    page[0][1] = ({"fig": fig}, {"table": df[:10]})

    page[0][2] = es.CardRowEqual(children=[{"fig": fig}, {"table": df[:10]}][::-1])

    page[0][3] = {"text": lorem}, {"table": df[:10]}

    page.save_html("page02.html")
    page.save_pdf("page02.pdf")


def example_03():
    page = es.Page(title="Markdown Page")
    page += "tests/resources/markdown.md"
    page.save_html("page03.html")
    page.save_pdf("page03.pdf")


def example_04():
    page = es.Page(title="Plotly Page")

    fig = px.scatter(data_frame=df, x="A", y="B")

    page[0][0] = df[:10], fig

    page[0][1] = ({"fig": fig}, {"table": df[:10]})

    page[0][2] = es.CardRowEqual(children=[{"fig": fig}, {"table": df[:10]}][::-1])

    page[0][3] = {"text": lorem}, {"table": df[:10]}

    page[0][4] = ({"fig": fig}, {"fig": fig})

    page.save_html("page04.html")
    page.save_pdf("page04.pdf")


if __name__ == "__main__":
    example_01()
    example_02()
    example_03()
    example_04()
