# README: Lambda Function for Transcoding Media Files with AWS MediaConvert

This Python code defines an AWS Lambda function that processes media files uploaded to an S3 bucket. The function uses AWS MediaConvert to transcode those files into MP4 format. Depending on the event type, the Lambda function handles either an S3 event or an SNS (Simple Notification Service) notification. Below is an overview of the key components and their functionality.

## Table of Contents
1. [Overview](#overview)
2. [Key Components](#key-components)
3. [Dependencies](#dependencies)
4. [Setup Instructions](#setup-instructions)
5. [How It Works](#how-it-works)
6. [Error Handling](#error-handling)
7. [Conclusion](#conclusion)

---

## Overview

This Lambda function listens for events from either an S3 bucket or an SNS topic:

- **S3 Event**: When a new media file is uploaded to the designated S3 bucket.
- **SNS Notification**: When MediaConvert completes a transcode job.

The function processes media files by invoking AWS MediaConvert to transcode the uploaded file into MP4 format, making it suitable for various media playback scenarios.

---

## Key Components

### 1. **S3 Bucket Event Trigger**
   - The Lambda function is triggered by an S3 event when a new media file (e.g., video file) is uploaded to a specified S3 bucket.
   - The event contains metadata about the uploaded file, such as the file name and its S3 location.

### 2. **SNS Notification**
   - If the Lambda function receives an SNS notification, it indicates that the MediaConvert job has completed.
   - This notification typically contains information about the status of the transcoding job, such as whether it succeeded or failed.

### 3. **AWS MediaConvert**
   - MediaConvert is an AWS service that allows for file transcoding (changing formats or optimizing media).
   - The Lambda function invokes the MediaConvert API to create a transcoding job, where the uploaded media file is converted into MP4 format.

### 4. **Lambda Function**
   - The Lambda function processes the events from S3 and SNS, handling the logic for invoking MediaConvert and updating the status of the transcoding job.

---

## Dependencies

The Lambda function requires the following Python packages:

- `boto3`: AWS SDK for Python, used to interact with S3, SNS, and MediaConvert.
- `json`: For parsing and handling event data.

Additionally, your Lambda function must have the necessary IAM permissions to interact with the following AWS services:
- S3
- SNS
- MediaConvert

---

## Setup Instructions

1. **Create an S3 Bucket**: Set up an S3 bucket to receive the media files for transcoding.
2. **Create an SNS Topic**: Set up an SNS topic to receive notifications from MediaConvert about job completion.
3. **Set Permissions**: Ensure that the Lambda function has the required IAM permissions to access S3, SNS, and MediaConvert.
4. **Deploy the Lambda Function**: Deploy the Lambda function with the correct event triggers (S3 or SNS).
5. **Configure MediaConvert**: Ensure you have an active MediaConvert account and set up the correct job templates for transcoding.

---

## How It Works

1. **S3 Event Trigger**:
   - When a file is uploaded to the designated S3 bucket, an S3 event is triggered.
   - The Lambda function receives the event, extracts the file details, and prepares a request to AWS MediaConvert to transcode the file into MP4 format.

2. **Invoke MediaConvert**:
   - The Lambda function invokes the MediaConvert API with the necessary parameters (such as the input file location in S3, output format, and output file location).
   - MediaConvert processes the file and stores the result in the specified output location in S3.

3. **SNS Notification**:
   - Once the MediaConvert job completes, an SNS notification is sent.
   - The Lambda function processes the notification, checks the job status (success or failure), and logs the result.

4. **File Availability**:
   - Once the file is successfully transcoded, it is made available in the designated output S3 bucket or location for further use.

---

## Error Handling

- If the S3 event is malformed or contains incorrect data, the Lambda function will log the error and can be configured to send notifications (e.g., via SNS or CloudWatch).
- In case of failure during the transcoding process, the Lambda function will check for error messages in the SNS notification and log the issue for troubleshooting.
- MediaConvert errors (e.g., unsupported formats) will be captured by the SNS notification, and the Lambda function will handle the failure accordingly.

---

## Conclusion

This Lambda function automates the process of transcoding media files uploaded to an S3 bucket using AWS MediaConvert. It listens for S3 events to trigger the transcoding job and processes SNS notifications to handle job completion. This solution simplifies media file conversion workflows by leveraging AWS serverless services, providing a scalable and cost-efficient solution for media file processing.

