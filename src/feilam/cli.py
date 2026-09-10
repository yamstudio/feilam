from click import command, group, option
from polars import col, concat_str, lit, read_excel, when
from polars.datatypes import Date, Decimal, Time, String, Int32

def _to_dms(dd_col: str):
  degree = col(dd_col).abs().floor().cast(Int32)
  minute = ((col(dd_col).abs() - degree) * 60).floor().cast(Int32)
  second = ((((col(dd_col).abs() - degree) * 60) - minute) * 60).cast(Decimal(scale=4, precision=6))
  return concat_str([degree, minute, second], separator=' ')

def _to_command():
  return concat_str([
    lit("exiftool -overwrite_original_in_place "),
    lit("-Model='"), col("Model"), lit("' "),
    lit("-Make='"), col("Make"), lit("' "),
    lit("-LensMake='"), col("Lens Make"), lit("' "),
    lit("-LensModel='"), col("Lens Model"), lit("' "),
    lit("-LensInfo='"), col("Lens Info"), lit("' "),
    lit("-ISO="), col("ISO"), lit(" "),
    lit("-FocalLength="), col("Focal Length"), lit(" "),
    lit("-ExposureTime='"), col("Exposure Time"), lit("' "), 
    lit("-FNumber='"), col("F Number"), lit("' "),
    lit("-DateTime='"), col("Date Time"), lit("' "),
    lit("-DateTimeOriginal='"), col("Date Time"), lit("' "),
    lit("-CreateDate='"), col("Date Time"), lit("' "),
    lit("-ModifyDate='"), col("Date Time"), lit("' "),
    lit("-OffsetTime='"), col("Time Zone"), lit("' "), 
    lit("-OffsetTimeOriginal='"), col("Time Zone"), lit("' "), 
    lit("-OffsetTimeDigitized='"), col("Time Zone"), lit("' "), 
    lit("-GPSLatitudeRef='"), col("GPS Latitude Ref"), lit("' "), 
    lit("-GPSLatitude='"), col("GPS Latitude DMS"), lit("' "), 
    lit("-GPSLongitudeRef='"), col("GPS Longitude Ref"), lit("' "), 
    lit("-GPSLongitude='"), col("GPS Longitude DMS"), lit("' "), 
    lit("-GPSAltitudeRef=0 "), 
    lit("-GPSAltitude="), col("GPS Altitude"), lit(" "),
    col("File Name")
  ])

@group()
def main():
  pass

@main.command()
@option('--source', '-s', required=True, help='Source parameters file')
@option('--model', required=True, default="NIKON F2")
@option('--make', required=True, default="NIKON CORPORATION")
def sync(source: str, model: str, make: str):
    """
    Sync parameters from the source file to the target file.
    """
    # Load parameters from the source file
    df = read_excel(
      source,
      schema_overrides={
        "Date": Date,
        "Time": Time,
        "F Number": String,
        "Exposure Time": String,
        "Focal Length": Int32,
        "GPS Latitude": Decimal(scale=12, precision=16),
        "GPS Longitude": Decimal(scale=12, precision=16),
        "GPS Altitude": Int32,
        "Lens Make": String,
        "Lens Model": String,
        "Lens Info": String,
        "ISO": Int32,
        "Time Zone": String,
        "Batch": Int32,
        "Seq": Int32,
        "Notes": String,
      }
    ).with_columns(
      concat_str(
        [
          col("Date").dt.strftime("%Y:%m:%d "),
          col("Time").dt.strftime("%H:%M:%S"),
          col("Time Zone")
        ]
      ).alias("Date Time"),
      when(col('GPS Latitude') >= 0)
        .then(lit('N'))
        .otherwise(lit('S'))
        .alias('GPS Latitude Ref'),
      _to_dms('GPS Latitude').alias('GPS Latitude DMS'),
      when(col('GPS Longitude') >= 0)
        .then(lit('E'))
        .otherwise(lit('W'))
        .alias('GPS Longitude Ref'),
      _to_dms('GPS Longitude').alias('GPS Longitude DMS'),
      lit(model).alias('Model'),
      lit(make).alias('Make'),
      concat_str(
        [
          col("Batch").cast(String).str.zfill(8),
          col("Seq").cast(String).str.zfill(4),
          lit(".JPG")
        ]
      ).alias("File Name")
    )

    # TODO: we probably should modify the file in place, not using exiftool
    for row in df.select(_to_command()).to_series().to_list():
      print(row)
