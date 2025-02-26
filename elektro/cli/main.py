import rich_click as click
import subprocess
import os


directory = os.getcwd()

file_path = os.path.dirname(__file__)


v1_file = """
projects:
  mikro:
    schema: http://localhost:8080/graphql
    documents: graphql/mikro/*/**.graphql
    extensions:
      turms:
        out_dir: mikro/api
        freeze:
          enabled: true
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
              - type: elektrorath.MikroRath
                key: rath
                description: "The mikro rath client"
            definitions:
              - type: subscription
                is_async: True
                use: elektrofuncs.asubscribe
              - type: query
                is_async: True
                use: elektrofuncs.aexecute
              - type: mutation
                is_async: True
                use: elektrofuncs.aexecute
              - type: subscription
                use: elektrofuncs.subscribe
              - type: query
                use: elektrofuncs.execute
              - type: mutation
                use: elektrofuncs.execute
        processors:
          - type: turms.processors.black.BlackProcessor
        scalar_definitions:
          XArrayInput: elektroscalars.XArrayInput
          File: elektroscalars.File
          ImageFile: elektroscalars.File
          Upload: elektroscalars.Upload
          ModelData: elektroscalars.ModelData
          ModelFile: elektroscalars.ModelFile
          ParquetInput: elektroscalars.ParquetInput
          Store: elektroscalars.Store
          Parquet: elektroscalars.Parquet
          ID: rath.scalars.ID
          MetricValue: elektroscalars.MetricValue
          FeatureValue: elektroscalars.FeatureValue
        additional_bases:
          Representation:
            - elektrotraits.Representation
          Table:
            - elektrotraits.Table
          Omero:
            - elektrotraits.Omero
          Objective:
            - elektrotraits.Objective
          Position:
            - elektrotraits.Position
          Stage:
            - elektrotraits.Stage
          ROI:
            - elektrotraits.ROI
          InputVector:
            - elektrotraits.Vectorizable
"""


@click.group()
def cli():
    pass


@cli.command()
def version():
    """Shows the current version of mikro"""


@cli.command()
def generate():
    """Generates the mikro api"""
    with open(f"{file_path}/../graphql.config.yaml", "w") as f:
        f.write(v1_file)
    subprocess.run(
        ["turms", "generate", "--config", f"{file_path}/../graphql.config.yaml"]
    )
    os.remove(f"{file_path}/../graphql.config.yaml")


if __name__ == "__main__":
    cli()
