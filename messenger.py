import json
import requests
from config import CONFIG

def messaging_events(payload):
    data = json.loads(payload)

    # Make sure this is a page subscription
    if (data.get("object") == "page"):
        # Iterate over each entry
        # There may be multiple if batched
        for entry in data.get("entry"):
            page_id = entry.get("id")
            time = entry.get("time")

            messaging_events = entry.get("messaging")
            for event in messaging_events:
                yield event


def received_authentication(event):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")
    time_of_auth = event.get("timestamp")

    pass_through_param = event.get("optin", {}).get("ref")

    print("Received authentication for user %s and page %s with pass "
          "through param '%s' at %s" % (sender_id, recipient_id, pass_through_param, time_of_auth))

    send_message(sender_id, "Authentication successful")


def received_message(event):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")
    time_of_message = event.get("timestamp")
    message = event.get("message", {})
    print("Received message for user %s and page %s at %s with message:"
          % (sender_id, recipient_id, time_of_message))
    print(message)

    is_echo = message.get("is_echo")
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")

    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")

    if is_echo:
        print("Received echo for message %s and app %s with metadata %s" % (message_id, app_id, metadata))
        return None
    elif quick_reply:
        quick_reply_payload = quick_reply.payload
        print("uick reply for message %s with payload %s" % (message_id, quick_reply_payload))

        send_message(sender_id, "Quic reply tapped")



    if message_text:
        send_message(sender_id, message_text)
    elif message_attachments:
        send_message(sender_id, "Message with attachment received")


def received_delivery_confirmation(event):
    delivery = event.get("delivery", {})
    message_ids = delivery.get("mids")
    watermark = delivery.get("watermark")
    seq = delivery.get("seq")

    if message_ids:
        for message_id in message_ids:
            print("Received delivery confirmation for message ID: %s" % message_id)

    print("All message before %s were delivered." % watermark)


def received_postback(event):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")
    time_of_postback = event.get("timestamp")

    payload = event.get("postback", {}).get("payload")

    print("Received postback for user %s and page %s with payload '%s' at %s"
          % (sender_id, recipient_id, payload, time_of_postback))

    send_message(sender_id, "Postback called")


def received_message_read(event):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")
    watermark = event.get("read", {}).get("watermark")
    seq = event.get("read", {}).get("seq")

    print("Received message read event for watermark %s and sequence number %s" % (watermark, seq))


def received_account_link(event):
    sender_id = event.get("sender", {}).get("id")
    recipient_id = event.get("recipient", {}).get("id")
    status = event.get("account_linking", {}).get("status")
    auth_code = event.get("account_linking", {}).get("authorization_code")

    print("Received account link event with for user %s with status %s and auth code %s "
          % (sender_id, status, auth_code))



def send_message(recipient_id, text):
    # If we receive a text message, check to see if it matches any special
    # keywords and send back the corresponding example. Otherwise, just echo
    # the text we received.
    special_keywords = {
        "image": send_image,
        "gif": send_gif,
        "audio": send_audio,
        "video": send_video,
        "file": send_file,
        "button": send_button,
        "generic": send_generic,
        "receipt": send_receipt,
        "quick reply": send_quick_reply,
        "read receipt": send_read_receipt,
        "typing on": send_typing_on,
        "typing off": send_typing_off,
        "account linking": send_account_linking
    }

    if text in special_keywords:
        special_keywords[text](recipient_id)
    else:
        send_text_message(recipient_id, text)

def send_image(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": CONFIG['SERVER_URL'] + "/assets/rift.png"
                }
            }
        }
    })

def send_gif(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": CONFIG['SERVER_URL'] + "/assets/instagram_logo.gif"
                }
            }
        }
    })


def send_audio(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "audio",
                "payload": {
                    "url": CONFIG['SERVER_URL'] + "/assets/sample.mp3"
                }
            }
        }
    })

def send_video(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "video",
                "payload": {
                    "url": CONFIG['SERVER_URL'] + "/assets/allofus480.mov"
                }
            }
        }
    })

def send_file(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "file",
                "payload": {
                    "url": CONFIG['SERVER_URL'] + "/assets/test.txt"
                }
            }
        }
    })

def send_button(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "This is test text",
                    "buttons":[{
                        "type": "web_url",
                        "url": "https://www.oculus.com/en-us/rift/",
                        "title": "Open Web URL"
                    }, {
                        "type": "postback",
                        "title": "tigger Postback",
                        "payload": "DEVELOPED_DEFINED_PAYLOAD"
                    }, {
                        "type": "phone_number",
                        "title": "Call Phone Number",
                        "payload": "+16505551234"
                    }]
                }
            }
        }
    })

def send_generic(recipient):
    call_send_api({
       "recipient": {
           "id": recipient
       },
       "message": {
           "attachment": {
               "type": "template",
               "payload": {
                   "template_type": "generic",
                   "elements": [{
                       "title": "rift",
                       "subtitle": "Next-generation virtual reality",
                       "item_url": "https://www.oculus.com/en-us/rift/",
                       "image_url": CONFIG['SERVER_URL'] + "/assets/rift.png",
                       "buttons": [{
                           "type": "web_url",
                           "url": "https://www.oculus.com/en-us/rift/",
                           "title": "Open Web URL"
                       }, {
                           "type": "postback",
                           "title": "Call Postback",
                           "payload": "Payload for first bubble",
                       }],
                   }, {
                       "title": "touch",
                       "subtitle": "Your Hands, Now in VR",
                       "item_url": "https://www.oculus.com/en-us/touch/",
                       "image_url": CONFIG['SERVER_URL'] + "/assets/touch.png",
                       "buttons": [{
                           "type": "web_url",
                           "url": "https://www.oculus.com/en-us/touch/",
                           "title": "Open Web URL"
                       }, {
                           "type": "postback",
                           "title": "Call Postback",
                           "payload": "Payload for second bubble",
                       }]
                   }]
               }
           }
       }
    })

def send_receipt(recipient):
    receipt_id = "order1357";
    call_send_api({
       "recipient": {
           "id": recipient
       },
       "message": {
           "attachment": {
               "type": "template",
               "payload": {
                   "template_type": "receipt",
                   "recipient_name": "Peter Chang",
                   "order_number": receipt_id,
                   "currency": "USD",
                   "payment_method": "Visa 1234",
                   "timestamp": "1428444852",
                   "elements": [{
                       "title": "Oculus Rift",
                       "subtitle": "Includes: headset, sensor, remote",
                       "quantity": 1,
                       "price": 599.00,
                       "currency": "USD",
                       "image_url": CONFIG['SERVER_URL'] + "/assets/riftsq.png"
                   }, {
                       "title": "Samsung Gear VR",
                       "subtitle": "Frost White",
                       "quantity": 1,
                       "price": 99.99,
                       "currency": "USD",
                       "image_url": CONFIG['SERVER_URL'] + "/assets/gearvrsq.png"
                   }],
                   "address": {
                       "street_1": "1 Hacker Way",
                       "street_2": "",
                       "city": "Menlo Park",
                       "postal_code": "94025",
                       "state": "CA",
                       "country": "US"
                   },
                   "summary": {
                       "subtotal": 698.99,
                       "shipping_cost": 20.00,
                       "total_tax": 57.67,
                       "total_cost": 626.66
                   },
                   "adjustments": [{
                       "name": "New Customer Discount",
                       "amount": -50
                   }, {
                       "name": "$100 Off Coupon",
                       "amount": -100
                   }]
               }
           }
       }
    })

def send_quick_reply(recipient):
    call_send_api({
       "recipient": {
           "id": recipient
       },
       "message": {
           "text": "What's your favorite movie genre?",
           "metadata": "DEVELOPER_DEFINED_METADATA",
           "quick_replies": [
               {
                   "content_type":"text",
                   "title":"Action",
                   "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_PICKING_ACTION"
               },
               {
                   "content_type":"text",
                   "title":"Comedy",
                   "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_PICKING_COMEDY"
               },
               {
                   "content_type":"text",
                   "title":"Drama",
                   "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_PICKING_DRAMA"
               }
           ]
       }
    })

def send_read_receipt(recipient):
   call_send_api({
       "recipient": {
           "id": recipient
       },
       "sender_action": "mark_seen"
   })

def send_typing_on(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "sender_action": "typing_on"
    })

def send_typing_off(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "sender_action": "typing_off"
    })

def send_account_linking(recipient):
    call_send_api({
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Welcome. Link your account.",
                    "buttons":[{
                        "type": "account_link",
                        "url": CONFIG['SERVER_URL'] + "/authorize"
                    }]
                }
            }
        }
    })

def send_text_message(recipient, text):
    call_send_api({
        "recipient": {"id": recipient},
        "message": {"text": text, "metadata": "DEVELOPER_DEFINED_METADATA"}
    })

def call_send_api(data):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": CONFIG['FACEBOOK_TOKEN']},
        data=json.dumps(data),
        headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print r.text