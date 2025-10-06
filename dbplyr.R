library(DBI)
library(dbplyr)
library(dplyr)

con <- dbConnect(
  odbc::odbc(),
  Driver = "Cloudera ODBC Driver for Impala",
  Host = "impala-host.example.com",
  Port = 21050,
  AuthMech = 1,
  KrbServiceName = "impala",
  KrbHostFQDN = "impala-host.example.com",
  KrbRealm = "EXAMPLE.COM",
  SSL = 1,
  TrustedCerts = "/etc/ssl/certs/ca-bundle.pem",
  Min_TLS = "1.2"
)

tbl(con, in_schema("analytics_db", "events")) |>
  summarise(n = n()) |>
  collect()
