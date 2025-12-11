import json
import boto3
import uuid

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("links")

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    long_url = body.get("url")

    if not long_url:
        return {"statusCode": 400, "body": "Missing URL"}

    short_id = body.get("custom") or str(uuid.uuid4())[:6]

    table.put_item(
        Item={
            "short_id": short_id,
            "long_url": long_url,
            "paid": bool(body.get("custom"))
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "short_url": f"https://example.com/{short_id}"
        })
    }
