import os
from dotenv import load_dotenv

import boto3
from langchain_aws import ChatBedrock

load_dotenv()

# client=boto3.client(service_name= os.environ['SERVICE_NAME'],
#                     region_name= os.environ['REGION_NAME'])
# LLM =ChatBedrock(model_id= os.environ['MODEL_ID'], client=client,
#                  model_kwargs={'temperature':0.1,'top_p':0.4})

client=boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
LLM=ChatBedrock(model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0", client=client, model_kwargs={'temperature':0.1,'top_p':0.4})

# print(os.environ['SERVICE_NAME'])