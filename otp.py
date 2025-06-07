import requests

phone_number_id = "701898626331512"
access_token = "EAAKGCXNgSyIBO2QiZCceqHMtgLQ1kBN2xwKOX6ErKrW5kDnPwxXsKuka2jJPcTMxEtii8aiZCxhUc8J2IbZBzBO19qJND3g3eTDQC8I5KO6BpB1TKw1h9QoUOnku7NbYaZBZB3igwjrZCFl6ybPoJGoCxnCg74z7kVbrxTN3TTTQZBKhQSyZCqgfaVbHUvLAn2i2PTLfjVQirEe5AV6jHZBBxqRBG0h3DSHZBA"
recipient_number = "916261127310"

url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

otp_code = "123456"  # You can replace this dynamically

payload = {
    "messaging_product": "whatsapp",
    "to": recipient_number,
    "type": "template",
    "template": {
        "name": "send_otp_us",  # Make sure this matches your template name exactly
        "language": {
            "code": "en_US"  # Ensure this matches the language code of your template
        },
        "components": [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": otp_code
                    }
                ]
            }
        ]
    }
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=payload)

print("Status Code:", response.status_code)
print("Response:", response.text)
