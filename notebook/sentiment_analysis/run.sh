#!/bin/bash
twitterscraper 😄 --lang ja -o happy.json &
twitterscraper 😢 --lang ja -o sad.json &
twitterscraper 😠 --lang ja -o angry.json &
twitterscraper 🤮 --lang ja -o disgust.json &
twitterscraper 🤢  --lang ja -o disgust2.json &
twitterscraper 😨 --lang ja -o fear.json &
twitterscraper 😲 --lang ja -o surprise.json &

wait;

echo "Done!:twitterscraper"
