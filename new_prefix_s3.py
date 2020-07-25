# using pandas to generate the date range
import pandas as pd

# using boto3 to connect with s3
import boto3

###########################################################

"""
Generate the dates that you need

The date format is:
%b: Returns the first three characters of the month name. In our example, it returned "Sep"
%d: Returns day of the month, from 1 to 31. In our example, it returned "15".
%Y: Returns the year in four-digit format. In our example, it returned "2018".
%H: Returns the hour. In our example, it returned "00".
%M: Returns the minute, from 00 to 59. In our example, it returned "00".
%S: Returns the second, from 00 to 59. In our example, it returned "00".
%a: Returns the first three characters of the weekday, e.g. Wed.
%A: Returns the full name of the weekday, e.g. Wednesday.
%B: Returns the full name of the month, e.g. September.
%w: Returns the weekday as a number, from 0 to 6, with Sunday being 0.
%m: Returns the month as a number, from 01 to 12.
%p: Returns AM/PM for time.
%y: Returns the year in two-digit format, that is, without the century. For example, "18" instead of "2018".
%f: Returns microsecond from 000000 to 999999.
%Z: Returns the timezone.
%z: Returns UTC offset.
%j: Returns the number of the day in the year, from 001 to 366.
%W: Returns the week number of the year, from 00 to 53, with Monday being counted as the first day of the week.
%U: Returns the week number of the year, from 00 to 53, with Sunday counted as the first day of each week.
%c: Returns the local date and time version.
%x: Returns the local version of date.
%X: Returns the local version of time.
"""


def generate_dates(startDate, endDate, format_="%Y%m%d"):
	dates = pd.date_range(start=startDate, end=endDate).strftime(format_).to_list()
	return dates

dates = generate_dates("20200501", "20200514")
	
# Initialize the bucket
s3 = boto3.resource("s3")
bucket_name = "datavisor-staging-blued-cn"
my_bucket = s3.Bucket(bucket_name)


# Initialize the directory

# the directory name under the bucket
first_level_in = "rawdata_sdkRetune/"

# usually it is the date
second_level_in = dates

# it is the directory under a specific date
third_level_in = ["rawlog."+date+"_000000.json/" for date in dates]
# print(third_level_in[:4])
### e.g. output: ['rawlog.20200501_000000.json/', 'rawlog.20200502_000000.json/', 'rawlog.20200503_000000.json/', 'rawlog.20200504_000000.json/']

# the prefix of the fileName, usually it is rawlog.20200501_000000.
out_prefix = ["rawlog."+date+"_000000.sdk." for date in dates]
# print(out_prefix[:4])
### e.g. output: ['rawlog.20200501_000000.sdk.', 'rawlog.20200502_000000.sdk.', 'rawlog.20200503_000000.sdk.', 'rawlog.20200504_000000.sdk.']

def mv_files(first_level_in, source_path, file_prefix_out, date):
    # time is the date folder
    print("Processing: ", date)
    # e.g. "rawdata_sdkRetune/20200501/rawlog.20200501_000000.json/"
    prefix = first_level_in + date + "/" + source_path
    
    # iterate all files under the path of prefix
    for object_summary in my_bucket.objects.filter(Prefix=prefix):
        # get the fileName with full path
        from_key = object_summary.key
        # skip if the fileName is not qualified
        if not from_key.endswith(".json.gz"):
            continue
            
        # get the file name without directory
        filename = from_key.split("/")[-1]
        # construct the new fileName
        new_filename = file_prefix_out + filename
        new_filename = new_filename.replace(".json.gz", ".gz")
        #destination path 
        dest_key = "rawdata_sdkRetune/" + date + "/" + new_filename
        
        #source path 
        copy_source_path = bucket_name + "/" + from_key
        s3.Object(bucket_name, dest_key).copy_from(CopySource=copy_source_path)
    print("Completed: ", date)

# copy
for i in range(len(dates)):
    mv_files(first_level_in, third_level_in[i], out_prefix[i], dates[i])














