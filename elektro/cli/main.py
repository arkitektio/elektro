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
              - type: mikro_nextrath.MikroRath
                key: rath
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
          XArrayInput: mikro_nextscalars.XArrayInput
          File: mikro_nextscalars.File
          ImageFile: mikro_nextscalars.File
          Upload: mikro_nextscalars.Upload
          ModelData: mikro_nextscalars.ModelData
          ModelFile: mikro_nextscalars.ModelFile
          ParquetInput: mikro_nextscalars.ParquetInput
          Store: mikro_nextscalars.Store
          Parquet: mikro_nextscalars.Parquet
          ID: rath.scalars.ID
          MetricValue: mikro_nextscalars.MetricValue
          FeatureValue: mikro_nextscalars.FeatureValue
        additional_bases:
          Representation:
            - mikro_nexttraits.Representation
          Table:
            - mikro_nexttraits.Table
          Omero:
            - mikro_nexttraits.Omero
          Objective:
            - mikro_nexttraits.Objective
          Position:
            - mikro_nexttraits.Position
          Stage:
            - mikro_nexttraits.Stage
          ROI:
            - mikro_nexttraits.ROI
          InputVector:
            - mikro_nexttraits.Vectorizable
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
