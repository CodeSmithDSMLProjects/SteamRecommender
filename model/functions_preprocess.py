import boto3
from botocore.exceptions import ClientError
import os
import pickle
import logging
import io

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

def upload_file(model, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    # if object_name is None:
    #     object_name = os.path.basename(file_name)

    
    # serialized_model = pickle.dumps(model)
    sess = boto3.Session(
        aws_access_key_id = os.environ["ACCESS_KEY"],
        aws_secret_access_key= os.environ["SECRET_KEY"]
    )
    s3client = sess.resource('s3')  


    # Upload the file
    # s3_client = boto3.resource('s3')
    try:
        pickle_buffer = io.BytesIO()
        model.to_pickle(pickle_buffer)
        response = s3client.Object(bucket,object_name).put(Body=pickle_buffer.getvalue())
    except ClientError as e:
        logging.error(e)
        return False
    return True
