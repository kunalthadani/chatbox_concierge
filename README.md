# Dining Concierge Chatbot - Cloud Computing and Big Data (Fall 2024) Assignment

This repository contains the code and documentation for implementing a serverless, microservice-driven web application that serves as a Dining Concierge chatbot. The chatbot interacts with users through conversation, collecting dining preferences and providing restaurant suggestions.

[link to the chatbot](http://chatbotkmt9501.s3-website-us-east-1.amazonaws.com/)
## Project Overview

The goal of this project is to build and deploy a dining concierge chatbot that interacts with users and provides restaurant suggestions based on user preferences such as location, cuisine, time, party size, and email. This application is built using a variety of AWS services, including:
- Amazon S3 for hosting the frontend
- API Gateway for API management
- Lambda for serverless computing
- Amazon Lex for natural language processing and conversation handling
- DynamoDB for data storage
- SQS for messaging
- SES for sending emails
- ElasticSearch for fast search capabilities

## Features

1. **Frontend:**
   - A simple web-based frontend hosted on AWS S3 that allows users to interact with the chatbot.

2. **API Backend:**
   - API Gateway that serves as the entry point for the chatbot API.
   - A Lambda function that processes user input and sends boilerplate responses initially.
   - AWS SDK is used to call the Lex chatbot and integrate it into the API.

3. **Chatbot:**
   - Amazon Lex powers the chatbot with the following intents:
     - `GreetingIntent`: Welcomes the user.
     - `ThankYouIntent`: Responds to user gratitude.
     - `DiningSuggestionsIntent`: Collects information from the user to provide restaurant suggestions.
   - The chatbot gathers information such as location, cuisine, time, number of people, and email.
   - The data collected is pushed to an SQS queue.

4. **Data Handling:**
   - Restaurant data (e.g., name, address, rating) is scraped from the Yelp API for Manhattan.
   - Restaurants are stored in DynamoDB and ElasticSearch.
   - DynamoDB contains full restaurant information.
   - ElasticSearch stores partial information (restaurant ID, cuisine) to facilitate fast searching.

5. **Suggestions Module:**
   - A Lambda function acts as a queue worker that processes messages from the SQS queue.
   - This function retrieves restaurant suggestions from ElasticSearch and DynamoDB, formats the suggestions, and sends them to the user via email using Amazon SES.

6. **Automation:**
   - CloudWatch or EventBridge is used to trigger the Lambda function for sending restaurant recommendations automatically.

7. **Extra Credit:**
   - Implementing stateful interaction where the chatbot remembers the user's last search (location and cuisine) and automatically provides suggestions upon the next conversation.

## Getting Started

### Prerequisites

- AWS Account with appropriate permissions
- Node.js (for frontend development)
- Python (for Lambda functions)
- Access to Yelp API for scraping restaurant data

### Setup Instructions

1. **Frontend Deployment:**
   - Clone the frontend starter repository from: `https://github.com/ndrppnc/cloud-hw1-starter`
   - Follow the [AWS S3 Hosting Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html) to host the frontend.
   - Ensure CORS is enabled for the S3 bucket to allow interaction with the backend API.

2. **API Gateway and Lambda Setup:**
   - Import the Swagger specification from `https://github.com/001000001/aics-columbia-s2018/blob/master/aics-swagger.yaml` into API Gateway.
   - Set up the API to trigger Lambda functions.
   - Implement Lambda (LF0) with boilerplate responses for testing (e.g., “I’m still under development”).

3. **Amazon Lex Chatbot:**
   - Create a Lex bot with three intents: `GreetingIntent`, `ThankYouIntent`, and `DiningSuggestionsIntent`.
   - Set up a Lambda function (LF1) to handle these intents, especially the `DiningSuggestionsIntent`, which gathers user preferences.
   - Test the bot through the Lex console.

4. **Yelp API Integration:**
   - Scrape restaurant data from the Yelp API and store the information in DynamoDB.
   - Use the following data fields for each restaurant: `Business ID, Name, Address, Coordinates, Number of Reviews, Rating, Zip Code`.
   - Store partial data in ElasticSearch (`RestaurantID`, `Cuisine`).

5. **Queue and Email Module:**
   - Create an SQS queue (Q1) to handle dining requests.
   - Implement a Lambda function (LF2) that retrieves a restaurant suggestion based on the user's preferences and sends an email via Amazon SES.
   - Set up automated triggers using CloudWatch or EventBridge to process SQS messages.

6. **ElasticSearch Setup:**
   - Create an ElasticSearch instance and index for restaurants.
   - Store partial restaurant information for fast querying based on cuisine.

### Running the Application

1. **Interaction Flow:**
   - User interacts with the chatbot via the frontend.
   - The chatbot collects user information, triggers Lambda functions, and pushes the request to an SQS queue.
   - A separate Lambda function fetches restaurant suggestions from DynamoDB and ElasticSearch, then sends the results via email using SES.

2. **Testing and Debugging:**
   - Use the Lex console to test chatbot responses.
   - Use AWS CloudWatch for Lambda logs and troubleshooting.


## Resources

- [Amazon S3 Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-import-api.html)
- [Amazon Lex Documentation](https://docs.aws.amazon.com/lex/latest/dg/getting-started.html)
- [Yelp API](https://www.yelp.com/developers/documentation/v3)
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)
- [Amazon SES](https://aws.amazon.com/ses/)
- [Amazon ElasticSearch](https://aws.amazon.com/elasticsearch-service/)
