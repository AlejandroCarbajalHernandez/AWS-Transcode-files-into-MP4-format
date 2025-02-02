import boto3
import os
from urllib.parse import unquote_plus

# Configura tus variables de entorno en Lambda para almacenar los detalles de MediaConvert
MEDIACONVERT_ROLE = os.environ['MEDIACONVERT_ROLE']
MEDIA_BUCKET = os.environ['MEDIA_BUCKET']
MEDIACONVERT_TEMPLATE_NAME = os.environ['MEDIACONVERT_TEMPLATE_NAME']
PROCESSED_SUFFIX = '_processed'

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    for record in event['Records']:
        # Filtrar eventos s3:ObjectCreated:Copy
        if 'eventName' in record and record['eventName'] == 'ObjectCreated:Copy':
            print(f"Evento de copia detectado para el archivo {record['s3']['object']['key']}. Saltando...")
            continue

        if 's3' in record:
            # Proceso original cuando se sube un archivo a S3
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])

            # Ignorar archivos ya procesados
            if key.endswith(PROCESSED_SUFFIX + '.mp4') or 'processed' in key:
                print(f"El archivo {key} ya ha sido procesado. Saltando...")
                continue

            # Filtrar por tipo de archivo si es necesario
            if not key.lower().endswith(('.mp4', '.mov', '.avi')):
                print(f"El archivo {key} no es un tipo de archivo soportado. Saltando...")
                continue

            # Input file S3 URL
            input_s3_url = f"s3://{bucket}/{key}"

            # Output file S3 URL (agregamos el sufijo _processed)
            output_key = key.rsplit('.', 1)[0] + PROCESSED_SUFFIX + '.mp4'
            output_s3_url = f"s3://{bucket}/{output_key}"

            # Create the job
            job_metadata = {
                'input_s3_url': input_s3_url,
                'output_s3_url': output_s3_url
            }

            job_settings = create_job_settings(input_s3_url, output_s3_url)

            mediaconvert_client = boto3.client('mediaconvert', endpoint_url=get_mediaconvert_endpoint())
            job = mediaconvert_client.create_job(
                Role=MEDIACONVERT_ROLE,
                Settings=job_settings,
                UserMetadata=job_metadata
            )

            print(f"Created MediaConvert job: {job['Job']['Id']}")

        elif 'Sns' in record:
            # Proceso cuando se recibe una notificación de SNS
            message = json.loads(record['Sns']['Message'])
            if 'detail' in message:
                output_key = message['detail']['outputGroupDetails'][0]['outputDetails'][0]['outputFilePaths'][0].split(f's3://{MEDIA_BUCKET}/')[1]
                original_key = message['detail']['userMetadata']['input_s3_url'].split(f's3://{MEDIA_BUCKET}/')[1]

                # Verificar si el archivo procesado existe
                if file_exists(s3_client, MEDIA_BUCKET, output_key):
                    print(f"El archivo procesado {output_key} ha sido creado exitosamente.")
                    # Eliminar el archivo original después de la transcodificación
                    delete_original_file(s3_client, MEDIA_BUCKET, original_key)
                else:
                    print(f"El archivo procesado {output_key} no se encontró. No se eliminará el archivo original {original_key}.")

def get_mediaconvert_endpoint():
    mediaconvert_client = boto3.client('mediaconvert')
    endpoints = mediaconvert_client.describe_endpoints()
    return endpoints['Endpoints'][0]['Url']

def create_job_settings(input_s3_url, output_s3_url):
    output_destination = output_s3_url.rsplit('/', 1)[0] + '/' + output_s3_url.rsplit('/', 1)[-1]
    
    return {
        "TimecodeConfig": {
            "Source": "ZEROBASED"
        },
        "OutputGroups": [
            {
                "CustomName": "videos",
                "Name": "File Group",
                "Outputs": [
                    {
                        "ContainerSettings": {
                            "Container": "MP4",
                            "Mp4Settings": {}
                        },
                        "VideoDescription": {
                            "CodecSettings": {
                                "Codec": "H_264",
                                "H264Settings": {
                                    "MaxBitrate": 5000000,
                                    "EntropyEncoding": "CABAC",
                                    "RateControlMode": "QVBR",
                                    "CodecProfile": "MAIN",
                                    "SceneChangeDetect": "TRANSITION_DETECTION",
                                    "QualityTuningLevel": "SINGLE_PASS"
                                }
                            }
                        },
                        "AudioDescriptions": [
                            {
                                "AudioSourceName": "Audio Selector 1",
                                "CodecSettings": {
                                    "Codec": "AAC",
                                    "AacSettings": {
                                        "Bitrate": 96000,
                                        "CodingMode": "CODING_MODE_2_0",
                                        "SampleRate": 44100
                                    }
                                }
                            }
                        ]
                    }
                ],
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {
                        "Destination": output_destination,
                        "DestinationSettings": {
                            "S3Settings": {
                                "StorageClass": "STANDARD"
                            }
                        }
                    }
                }
            }
        ],
        "Inputs": [
            {
                "FileInput": input_s3_url,
                "AudioSelectors": {
                    "Audio Selector 1": {
                        "DefaultSelection": "DEFAULT"
                    }
                },
                "VideoSelector": {},
                "TimecodeSource": "ZEROBASED"
            }
        ]
    }

def delete_original_file(s3_client, bucket, key):
    try:
        response = s3_client.delete_object(Bucket=bucket, Key=key)
        print(f"Archivo original {key} eliminado con éxito.")
    except Exception as e:
        print(f"Error al eliminar el archivo original {key}: {str(e)}")

def file_exists(s3_client, bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except s3_client.exceptions.ClientError:
        return False
