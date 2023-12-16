import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, InlineQueryHandler
from googleapiclient.discovery import build
import openai  # Make sure to install the 'openai' library

# Telegram bot token
TELEGRAM_TOKEN = '6901465199:AAHgubSGrdkl1bYpPKbkdlRJg0qmKVQE8GE'

# Google API credentials
GOOGLE_API_KEY = 'AIzaSyBAFiHmyZnoh5An7qf5njlRP0_xHsgeW7c'
FACT_CHECK_API_VERSION = 'v1alpha1'
FACT_CHECK_API_SERVICE_NAME = 'factchecktools'

# Set your OpenAI GPT-3 API key
OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to FactHunter Bot! Text me a piece of news, and I will check if it is fake.\nfeel free to dm me at whatsapp on 8309173896')

def check_fake_news(update: Update, context: CallbackContext) -> None:
    # Get the user's message
    user_message = update.message.text

    # Log the user's message
    log_user_message(user_message, update.message.from_user)

    # Use Google Fact Check Explorer API to check the claim
    result = check_fact_check_explorer(user_message)

    # Include the feedback message
    feedback_message = "Feel free to give feedback at WhatsApp on 8309173896."

    # Build the response message
    response_message = f"\nResult: {result}\n\n{feedback_message}"

    # Send the result back to the user
    update.message.reply_text(response_message)

def log_user_message(message: str, user_info) -> None:
    # You can customize the logging mechanism (e.g., save to a file, database, etc.)
    # Here, we simply print the user's message and information to the console
    print(f"User Info: {user_info}\n")

def check_fact_check_explorer(claim: str) -> str:
    service = build(FACT_CHECK_API_SERVICE_NAME, FACT_CHECK_API_VERSION, developerKey=GOOGLE_API_KEY)

    try:
        # Use the claim as the query to Fact Check Explorer API
        request = service.claims().search(query=claim)
        response = request.execute()

        # Check if any results are found
        if 'claims' in response:
            claims = response['claims']
            if claims:
                # Get the first claim and check its claimReview
                claim_review = claims[0].get('claimReview', [])
                if claim_review:
                    # Check the claim's claimReview for the result
                    result = claim_review[0].get('text', 'Result not available.')
                    publication_date = claim_review[0].get('publishDate', 'Date not available.')
                    url = claim_review[0].get('url', 'URL not available.')

                    response_message = f"\nClaim: {claim}\nURL: {url}"

                    return response_message

        # If no results are found, generate response using chatGPT
        chatgpt_response = generate_chatgpt_response(claim)
        return chatgpt_response

    except Exception as e:
        print(f"An error occurred: {e}")
        return 'An error occurred while processing the request.'

def generate_chatgpt_response(claim: str) -> str:
    # Use OpenAI GPT-3 to generate a response based on the claim
    prompt = f"Check the claim: {claim}. Provide relevant information."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )

    return response.choices[0].text.strip()

def inline_query(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    if not query:
        return

    results = []
    response_message = check_fact_check_explorer(query)

    results.append(
        InlineQueryResultArticle(
            id='1',
            title='Fake News Detector Result',
            input_message_content=InputTextMessageContent(response_message),
        )
    )

    update.inline_query.answer(results)

def main() -> None:
    # Create the Updater and pass it the bot's token
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))

    # Register a message handler to check for fake news
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_fake_news))

    # Register inline query handler
    dp.add_handler(InlineQueryHandler(inline_query))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
