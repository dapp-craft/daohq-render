
# Rendering Service

## Overview

This Python service is designed to render Discord messages as images and provide an endpoint for rendering external metrics. The service uses FastAPI for creating endpoints and Playwright for rendering HTML to images. Additionally, it includes a Discord bot to capture and send messages for rendering.


## Discord Bot

The service includes a Discord bot to capture messages, edits, and deletions.

### Bot Configuration

- **Token**: Set the `DISCORD_TOKEN` environment variable.
- **Intents**: The bot requires message and message content intents.

### Bot Events

- **on_message**: Captures new messages and sends them to the rendering service.
- **on_message_edit**: Captures message edits and updates the rendered image.
- **on_message_delete**: Deletes the rendered image when a message is deleted.

## Environment Variables

- `BACKEND_URL`: URL of the backend service.
- `SYSTEM_TOKEN`: System token for authorization.
- `DISCORD_TOKEN`: Discord bot token.
- `AWS_ACCESS_KEY_ID`: AWS access key ID for S3.
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key for S3.

## Running

1. Clone the repository.
2. Install dependencies:
   ```sh
   pip3 install -r requirements.txt
   ```
3. Run the service:
   ```sh
   python3 server.py
   ```

### Running via docker

1. Build docker image:
   ```sh
   docker build -t render .
   ```
2. Run container with all environment variables:
   ```sh
   docker run -d --network host \
        -e DISCORD_TOKEN=${DISCORD_TOKEN} \
        -e SYSTEM_TOKEN=${SYSTEM_TOKEN} \
        -e BACKEND_URL=${BACKEND_URL} \
        -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
        -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
        --name=render_container render
   ```

## Usage

### Rendering a Discord Message

Add your discord bot to channel which you want to parse and then send a new message

### Rendering Metrics

Send a POST request to `/metrics/image`.

- **Endpoint**: `/metrics/image`
- **Method**: POST
- **Description**: Renders external metrics as images.
- **Response**: JSON object containing the S3 URN of the rendered images.


## Editing Discord template

```
cd ./templates-src/discord
npm i
```

Edit `main.ts` file.

Build template: 

```
npm run build
```

Make sure template updated in `/static/discord` directory. And don't forget to commit it.
