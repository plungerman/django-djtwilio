from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """
    Send a dynamic reply to an incoming text message
    see:
    https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python?code-sample=code-generate-a-dynamic-twiml-message&code-language=Python&code-sdk-version=6.x
    """
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'hello':
        resp.message("Hi!")
    elif body == 'bye':
        resp.message("Goodbye")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
