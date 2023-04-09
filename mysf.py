from snowflake.snowpark import Session

connection_parameters = {
  "account": "ww82873.europe-west4.gcp",
  "user": "pawelek",
  "password": "!QA2ws3ed",
  "role": "ACCOUNTADMIN",
  "warehouse": "COMPUTE_WH",
  "database": "DEV",
  "schema": "PUBLIC"
}

session = Session.builder.configs(connection_parameters).create()
df = session.create_dataframe([[1, 2], [3, 4]], schema=["a", "b"])
df = df.filter(df.a > 1)
df.show()
pandas_df = df.to_pandas()  # this requires pandas installed in the Python environment
result = df.collect()
