import boto3
from botocore.exceptions import ClientError
import os


def select_n_components(var_ratio, goal_var=0.95):
    """

    Returns n_components needed for specified variance rate

    Args:
        var_ratio (array): Array containing the variance ratios
        goal_var (float): Desired variance ratio. Default = 0.95

    Returns:
        n_components (int): Number of components needed for desired variance
    """

    # Set initial variance explained so far
    total_variance = 0
    # Set initial number of features
    n_components = 0
    # For the explained variance of each feature:
    for explained_variance in var_ratio:
        # Add the explained variance to the total
        total_variance += explained_variance
        # Add one to the number of components
        n_components += 1
        # If we reach our goal level of explained variance:
        if total_variance >= goal_var:
            # End the loop
            break
    # Return the number of components
    return n_components

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
