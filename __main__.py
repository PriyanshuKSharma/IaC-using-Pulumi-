import pulumi
import pulumi_aws as aws
import os
import mimetypes
import uuid  # For generating unique resource names

# Create an AWS resource (S3 Bucket)
config = pulumi.Config()

# get the site_dir from the config file
site_dir = config.require("siteDir")

# create a bucket with the name my-bucket
bucket = aws.s3.Bucket("my-bucket", website={
    "index_document": "index.html"
})

# Iterate through all files in the site_dir
for file in os.listdir(site_dir):
    # Get the path of the file
    filepath = os.path.join(site_dir, file)

    # Get the mime type of the file
    mime_type, _ = mimetypes.guess_type(filepath)

    # Generate a unique name for the BucketObject to avoid duplicates
    unique_name = f"{file}-{str(uuid.uuid4())}"

    # Create a file in the bucket with the corresponding content type
    bucket_object = aws.s3.BucketObject(unique_name,
        bucket=bucket.id,
        source=pulumi.FileAsset(filepath),
        content_type=mime_type if mime_type else "application/octet-stream"  # Set mime type
    )

# Exporting the bucket name
pulumi.export("bucket_name", bucket.bucket)

# Exporting the website URL
pulumi.export('bucket_endpoint', pulumi.Output.concat("http://", bucket.website_endpoint))
