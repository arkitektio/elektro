from pydantic import Field
from koil.composition import Composition
from elektro.rath import ElektroRath
from elektro.datalayer import DataLayer


class Elektro(Composition):
    """The Mikro Composition

    This composition provides a datalayer and a rath for interacting with the
    mikro api and beyond

    You shouldn't need to create this directly, instead use the builder functions
    to generate a new instance of this composition.

    ```python

    from mikro import Mikro

    async def aget_token():
        return "XXXX"

    m = Mikro(
        datalayer= DataLayer(endpoint_url="s3.amazonaws.com", access_key="XXXX", secret_key="XXXX"),
        mikro = MikroRath(link=MikroLinkComposition(auth=AuthTokenLink(token_loader=aget_token)))),
    )
    ```
    """

    datalayer: DataLayer = Field(
        ..., description="The datalayer for interacting with the mikro api"
    )
    rath: ElektroRath

    def _repr_html_inline_(self):
        return f"<table><td>rath</td><td>{self.rath._repr_html_inline_()}</td></tr></table>"
