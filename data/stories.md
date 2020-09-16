## happy path
* greet
  - utter_greet
* mood_great
  - utter_happy

## sad path 1
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* affirm
  - utter_happy

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot

## restaurant story
* greet
  - utter_greet
* restaurant_search
  - utter_ask_location
* location
  - action_set_location
  - slot{"location": "Sangli"}
  - utter_ask_cuisine
* cuisine {"cuisine": "Pizza"}
  - slot{"cuisine": "Pizza"}
  - utter_affirm
  - action_show_restaurants
* goodbye
  - utter_goodbye

## deny cuisine
* greet
  - utter_greet
* restaurant_search
  - utter_ask_location
* location
  - action_set_location
  - slot{"location": "Mumbai"}
  - utter_ask_cuisine
* deny
  - utter_affirm
  - action_default_restaurants

## location cuisine
* greet
  - utter_greet
* location_cuisine
  - slot{"location": "Sangli"}
  - slot{"cuisine": "maharashtrian"}
  - utter_affirm
  - action_show_restaurants
* goodbye
  - utter_goodbye