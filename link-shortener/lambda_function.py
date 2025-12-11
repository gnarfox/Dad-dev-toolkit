import json
import boto3
import uuid

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("links")

def lambda_handler(event, context):

    route = event.get("routeKey", "")

    # GET redirect
    if route.startswith("GET "):
        short_id = event.get("pathParameters", {}).get("id")

        if not short_id:
            return {"statusCode": 400, "body": "Missing id"}

        result = table.get_item(Key={"short_id": short_id})

        if "Item" not in result:
            return {"statusCode": 404, "body": "Not found"}

        return {
            "statusCode": 302,
            "headers": {
                "Location": result["Item"]["long_url"]
            }
        }

    # POST create short link
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
            "short_url": f"https://8e04m45x85.execute-api.us-east-1.amazonaws.com/{short_id}"
        })
    }
