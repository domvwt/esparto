from esparto.layout import Page, Section, Row, Column
from esparto.content import Markdown, Image
from esparto.publish import publish


if __name__ == "__main__":
    content = Page(
        Section(
            Row(
                Column(
                    Markdown("* list item \n * list item"),
                    Markdown("> Quote!"),
                )
            ),
            Row(
                Column(
                    Image(
                        "/home/domvwt/repos/esparto/esparto/public/choosing-a-cat.jpg",
                        size=0.1,
                    ),
                ),
                Column(
                    Image(
                        "/home/domvwt/repos/esparto/esparto/public/choosing-a-cat.jpg",
                        size="auto",
                    )
                ),
            ),
        ),
        title="Regression Report",
    )

    publish(content)
