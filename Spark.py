from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MySparkApp") \
    .enableHiveSupport() \
    .config("hive.metastore.uris", "thrift://your-metastore-host:9083") \
    .getOrCreate()
