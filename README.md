# README: AWS Lambda Function for Media File Transcoding with AWS MediaConvert

This Python code is designed to be deployed as an AWS Lambda function. The function processes media files uploaded to an S3 bucket, automatically transcoding them into MP4 format using AWS MediaConvert. It also integrates with SNS to monitor the status of the transcoding process and handles various tasks based on the event type.

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Setup Instructions](#setup-instructions)
4. [Environment Variables](#environment-variables)
5. [How It Works](#how-it-works)
6. [Error Handling](#error-handling)
7. [Conclusion](#conclusion)

---

## Overview

This Lambda function is triggered by events from either an S3 bucket or an SNS topic. It works as follows:

- **S3 Event**: When a media file is uploaded to the specified S3 bucket, the function checks if the file is of an acceptable type (e.g., `.mp4`, `.mov`, `.avi`). If the file hasn't been processed yet, it initiates a transcoding job using AWS MediaConvert.
  
- **SNS Notification**: Once the transcoding job is complete, AWS MediaConvert sends a notification to an SNS topic. The Lambda function processes this notification, confirms that the transcoded file exists, and optionally deletes the original file.

---

## Key Features

- **File Type Filtering**: The Lambda function processes only video files with extensions `.mp4`, `.mov`, and `.avi`.
- **Job Creation with MediaConvert**: The function creates a MediaConvert job for transcoding the input media file into MP4 format.
- **SNS Notification Handling**: The function listens for SNS notifications, checks if the transcoded file is available, and handles post-processing steps like deleting the original file.
- **File Existence Check**: It ensures that the transcoded file exists before deleting the original.
- **Avoid Reprocessing**: Files that have already been processed are skipped to prevent unnecessary transcoding.

---

## Setup Instructions

1. **Create an S3 Bucket**: Create an S3 bucket where media files will be uploaded.
2. **Create an SNS Topic**: Set up an SNS topic for notifications from AWS MediaConvert about job completion.
3. **Create a MediaConvert Role**: Ensure you have a valid IAM role for MediaConvert with permissions to read from and write to the S3 bucket.
4. **Deploy Lambda Function**:
   - Create a Lambda function in the AWS console and upload the code.
   - Set up the function to be triggered by S3 events (e.g., `s3:ObjectCreated:Put`) and SNS notifications.
5. **Configure Environment Variables**: Set the following environment variables for the Lambda function:
   - `MEDIACONVERT_ROLE`: The ARN of the IAM role for MediaConvert.
   - `MEDIA_BUCKET`: The name of the S3 bucket where media files are stored.
   - `MEDIACONVERT_TEMPLATE_NAME`: The name of the MediaConvert job template you want to use.
   - `PROCESSED_SUFFIX`: The suffix appended to processed files (e.g., `_processed`).

---

## Environment Variables

Ensure that the following environment variables are set when deploying the Lambda function:

- **`MEDIACONVERT_ROLE`**: The IAM role ARN used by MediaConvert for transcoding jobs.
- **`MEDIA_BUCKET`**: The S3 bucket name where media files are uploaded and processed.
- **`MEDIACONVERT_TEMPLATE_NAME`**: The name of the job template used for transcoding.
- **`PROCESSED_SUFFIX`**: The suffix added to processed files (e.g., `_processed`).

---

## How It Works

### 1. **S3 Event Trigger**:
   - The Lambda function is triggered when a file is uploaded to the S3 bucket specified in the event.
   - The function checks if the uploaded file is a supported media format (e.g., `.mp4`, `.mov`, `.avi`) and not yet processed.
   - If valid, it initiates a transcoding job with MediaConvert, creating an MP4 file from the input.

### 2. **MediaConvert Job**:
   - The Lambda function creates a job in MediaConvert using the provided role and settings (like H.264 video codec and AAC audio codec).
   - MediaConvert processes the input file and outputs an MP4 file to the specified S3 location.

### 3. **SNS Notification**:
   - Once the transcoding job completes, MediaConvert sends an SNS notification.
   - The Lambda function receives the notification and checks if the output file exists.
   - If the transcoded file is found, the Lambda function deletes the original file.

### 4. **Post-Processing**:
   - If the transcoded file is successfully created, the original file is deleted to save space.
   - If the file is not found, the original file remains in the S3 bucket.

---

## Error Handling

- **File Already Processed**: Files that have already been processed are ignored by the Lambda function.
- **Unsupported File Types**: If a file does not meet the expected extensions (`.mp4`, `.mov`, `.avi`), it is skipped.
- **MediaConvert Job Failure**: If the MediaConvert job fails, the function checks the SNS notification for error details. You can configure additional logging and alerting for job failures.
- **File Deletion Errors**: If the Lambda function fails to delete the original file, it logs the error for troubleshooting.

---
## Summary
- The processed file is identified by the _processed suffix in its name (e.g., video_processed.mp4).
- The Lambda function checks if the uploaded file already has this suffix or contains the word processed in its name before starting the transcoding process.
- After transcoding, it uses the output filename (with _processed) to confirm that the file exists in S3 and is successfully transcoded. If found, it proceeds with cleanup by deleting the original file.
## Conclusion

This AWS Lambda function automates the transcoding of media files uploaded to an S3 bucket using AWS MediaConvert. It handles both S3 events and SNS notifications, ensuring that media files are efficiently converted into MP4 format while cleaning up the original files post-transcoding. This solution is highly scalable, cost-efficient, and easily integrates into serverless workflows for media processing.

