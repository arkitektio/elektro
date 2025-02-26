---
sidebar_position: 5
sidebar_label: "Turms"
---

# Mikro ❤️ Turms

### What is turms?

Turms is a graphql-codegen inspired code generator for python that generates fully typed and
serialized operations from your graphql schema. Just define your query in standard graphql syntax
and let turms create fully typed queries/mutation and subscriptions, that you can use in your favourite
IDE and with your favourite client like rath.

### Inspiration

GraphQL is a powerful query language.... TODO: WRITE STUFF HERE

### Isn't code generation bad?

No.

### Turms

Turms can generate pydantic models that are automatically validated through your schema and makes working with
graphql fragments and operations super easy.

Mikros api is almost entirely code generated through turms and this configuration.

```yaml
projects:
  mikro:
    schema: http://localhost:8080/graphql
    documents: graphql/*/**.graphql
    extensions:
      turms:
        out_dir: mikro/api
        freeze: True
        stylers:
          - type: turms.stylers.default.DefaultStyler
          - type: turms.stylers.appender.AppenderStyler
            append_fragment: "Fragment"
        plugins:
          - type: turms.plugins.enums.EnumsPlugin
          - type: turms.plugins.inputs.InputsPlugin
          - type: turms.plugins.fragments.FragmentsPlugin
          - type: turms.plugins.operations.OperationsPlugin
          - type: turms.plugins.funcs.FuncsPlugin
            global_kwargs:
              - type: mikro_nextmikro_nextMikroRath
                key: mikrorath
                description: "The mikro rath client"
            definitions:
              - type: subscription
                is_async: True
                use: mikro_nextfuncs.asubscribe
              - type: query
                is_async: True
                use: mikro_nextfuncs.aexecute
              - type: mutation
                is_async: True
                use: mikro_nextfuncs.aexecute
              - type: subscription
                use: mikro_nextfuncs.subscribe
              - type: query
                use: mikro_nextfuncs.execute
              - type: mutation
                use: mikro_nextfuncs.execute
        processors:
          - type: turms.processors.black.BlackProcessor
        scalar_definitions:
          XArray: mikro_nextscalars.XArray
          File: mikro_nextscalars.File
          ImageFile: mikro_nextscalars.File
          Upload: mikro_nextscalars.Upload
          DataFrame: mikro_nextscalars.DataFrame
          Store: mikro_nextscalars.Store
        additional_bases:
          Representation:
            - mikro_nexttraits.Representation
          Sample:
            - mikro_nexttraits.Sample
          Table:
            - mikro_nexttraits.Table
          OmeroFile:
            - mikro_nexttraits.OmeroFile
          Thumbnail:
            - mikro_nexttraits.Thumbnail
          Experiment:
            - mikro_nexttraits.Experiment
```

With this generation rath will generate fully typed classes for enums, fragments, operations and additionally
because we specify the RathFuncsPlugin, fully typed functions that we you can use in your code (ala useQuery, useMutation in apollo).

On running (in your terminal)

```bash
turms gen
```

Turms generates automatically this pydantic schema for you

```python title="api/schema.py"
from typing import Literal, List, Optional
from pydantic import Field, BaseModel
from enum import Enum
from rath.turms.funcs import aexecute, execute


class Beast(BaseModel):
    typename: Optional[Literal["Beast"]] = Field(alias="__typename")
    commonName: Optional[str]
    "a beast's name to you and I"
    taxClass: Optional[str]
    "taxonomy grouping"


class Get_beasts(BaseModel):
    beasts: Optional[List[Optional[Beast]]]

    class Meta:
        domain = "default"
        document = "fragment Beast on Beast {\n  commonName\n  taxClass\n}\n\nquery get_beasts {\n  beasts {\n    ...Beast\n  }\n}"


def get_beasts() -> List[Beast]:
    """get_beasts



    Arguments:

    Returns:
        Beast: The returned Mutation"""
    return execute(Get_beasts, {}).beasts


async def aget_beasts() -> List[Beast]:
    """get_beasts



    Arguments:

    Returns:
        Beast: The returned Mutation"""
    return (await aexecute(Get_beasts, {})).beasts
```

Which you can than use easily in your application code, like this

```python
from rath import Rath
from api import get_beasts

rath = Rath(AIOHttpLink(url="..."))

with rath:
    beasts = get_beasts()
    first_beast_name = beasts[0].commonName

```

Your Queries are now strongly typed, with comments from your schema.

:::info
RathFuncs is just a thin wrapper aorund the OperationsFuncsPlugin that comes with turms,
check out `rath.turms.funcs` for inspiraiton on writing your own.
:::
